import customtkinter as ctk
from services.prefs import Preferences
from pathlib import Path
from ui.mongo_view import MongoSection
from ui.minio_view import MinioSection
from ui.experiment_view import ExperimentSection

class LoginView(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("App View • CustomTkinter")
        # Window size will adapt to content via fit_to_content()

        # Prefs (sauvegarde/restauration)
        self.prefs = Preferences()

        # --- ROOT GRID ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- FRAME ---
        frm = ctk.CTkFrame(self, corner_radius=12)
        frm.grid(row=0, column=0, padx=16, pady=16, sticky="nsew")
        frm.grid_columnconfigure(0, weight=0)
        frm.grid_columnconfigure(1, weight=1)

        # Left stack: Mongo (top) then MinIO (bottom)
        self.mongo_section = MongoSection(frm, on_save=self.save_prefs, on_change=lambda: self.after(10, self.fit_to_content))
        self.mongo_section.grid(row=0, column=0, sticky="nsew", padx=12, pady=(8, 8))

        # --- EXPERIMENT FILES SECTION ---
        self.exp_section = ExperimentSection(frm, on_change=lambda: self.after(10, self.fit_to_content))
        self.exp_section.grid(row=0, column=1, rowspan=20, sticky="nsew", padx=12, pady=(8, 8))

        # --- MINIO SECTION (below Mongo on the left) ---
        self.minio_section = MinioSection(frm, on_save=self.save_prefs, on_change=lambda: self.after(10, self.fit_to_content))
        self.minio_section.grid(row=1, column=0, sticky="nsew", padx=12, pady=(8, 8))

        # Charger préférences + hook fermeture
        self.load_prefs()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        # Fit window to the current content
        self.after(50, self.fit_to_content)

    # --- HELPERS ---
    def toggle_uri(self):
        # Deprecated: handled inside MongoSection
        pass

    # --- Prefs ---
    def prefs_dict(self):
        data = {}
        data.update(self.mongo_section.get_prefs())
        data.update(self.exp_section.get_prefs())
        data.update(self.minio_section.get_prefs())
        return data

    def save_prefs(self):
        data = self.prefs_dict()
        self.prefs.save_without_password(data)
        # mot de passe via keyring si demandé (Mongo)
        self.prefs.save_password_if_allowed(
            remember=bool(data.get("remember_pwd")),
            user=data.get("user") or "default",
            password=self.mongo_section.get_password()
        )
        # minio secret via keyring
        minio_user_key = f"minio:{(data.get('minio_access_key') or 'default')}@{(data.get('minio_endpoint') or 'localhost')}"
        self.prefs.save_password_if_allowed(
            remember=bool(data.get("remember_minio", 0)),
            user=minio_user_key,
            password=self.minio_section.get_secret()
        )

    def load_prefs(self):
        data = self.prefs.load()
        # delegate to sections
        self.mongo_section.set_prefs(data, password_loader=lambda user: self.prefs.load_password_if_any(user=user))
        self.exp_section.set_prefs(data)
        self.minio_section.set_prefs(data, password_loader=lambda user: self.prefs.load_password_if_any(user=user))
        self.after(10, self.fit_to_content)

    def on_close(self):
        # Sauvegarde avant sortie
        self.save_prefs()
        self.destroy()

    # Experiment helpers moved into ExperimentSection

    # --- Window sizing helper ---
    def fit_to_content(self):
        try:
            self.update_idletasks()
            req_w = self.winfo_reqwidth()
            req_h = self.winfo_reqheight()
            min_w, max_w = 600, 1000
            min_h, max_h = 500, 900
            new_w = max(min(req_w, max_w), min_w)
            new_h = max(min(req_h, max_h), min_h)
            self.minsize(min_w, min_h)
            self.geometry(f"{new_w}x{new_h}")
        except Exception:
            pass

    # MinIO helpers moved into MinioSection
