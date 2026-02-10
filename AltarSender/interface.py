# app.py
import customtkinter as ctk
from pymongo import MongoClient
from pymongo.errors import PyMongoError
import urllib.parse

ctk.set_appearance_mode("system")      # "light" | "dark" | "system"
ctk.set_default_color_theme("blue")    # "blue" | "green" | "dark-blue"
ctk.deactivate_automatic_dpi_awareness()  # prevent alpha flicker/opacity when moving between monitors

class MongoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AltarSender — MongoDB Login")
        self.geometry("520x420")
        self.minsize(520, 420)

        # --- GRID ROOT ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- FRAME ---
        frm = ctk.CTkFrame(self, corner_radius=12, fg_color=("white", "#1f1f1f"))
        frm.grid(row=0, column=0, padx=16, pady=16, sticky="nsew")
        frm.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(frm, text="MongoDB Connection", font=("Segoe UI", 18, "bold")).grid(row=0, column=0, columnspan=2, pady=(12, 18))

        # --- INPUTS ---
        self.use_uri = ctk.CTkCheckBox(frm, text="Use a MongoDB URI (mongodb:// or mongodb+srv://)", command=self.toggle_uri)
        self.use_uri.grid(row=1, column=0, columnspan=2, sticky="w", padx=12, pady=(0,8))

        self.uri_entry = ctk.CTkEntry(frm, placeholder_text="mongodb://localhost:27017", width=380)
        self.uri_entry.grid(row=2, column=0, columnspan=2, sticky="ew", padx=12, pady=(0,12))
        self.uri_entry.configure(state="disabled")

        self.host_entry = ctk.CTkEntry(frm, placeholder_text="Host (e.g., localhost)")
        self.port_entry = ctk.CTkEntry(frm, placeholder_text="Port (e.g., 27017)")
        self.user_entry = ctk.CTkEntry(frm, placeholder_text="Username (optional)")
        self.pass_entry = ctk.CTkEntry(frm, placeholder_text="Password (optional)", show="•")
        self.db_entry   = ctk.CTkEntry(frm, placeholder_text="Database (e.g., admin)")

        self.host_entry.grid(row=3, column=0, sticky="ew", padx=(12,6), pady=6)
        self.port_entry.grid(row=3, column=1, sticky="ew", padx=(6,12), pady=6)
        self.user_entry.grid(row=4, column=0, sticky="ew", padx=(12,6), pady=6)
        self.pass_entry.grid(row=4, column=1, sticky="ew", padx=(6,12), pady=6)
        self.db_entry.grid(row=5, column=0, columnspan=2, sticky="ew", padx=12, pady=6)

        # TLS / Options simples
        self.tls_chk = ctk.CTkCheckBox(frm, text="TLS/SSL (recommended with mongodb+srv)")
        self.tls_chk.grid(row=6, column=0, columnspan=2, sticky="w", padx=12, pady=6)

        # --- ACTIONS ---
        btn_row = ctk.CTkFrame(frm, fg_color="transparent")
        btn_row.grid(row=7, column=0, columnspan=2, sticky="ew", padx=12, pady=(12,4))
        btn_row.grid_columnconfigure((0,1), weight=1)

        self.test_btn = ctk.CTkButton(btn_row, text="Test connection", command=self.test_connection)
        self.test_btn.grid(row=0, column=0, sticky="ew", padx=(0,6))

        self.clear_btn = ctk.CTkButton(btn_row, text="Clear", fg_color="gray", hover_color="#6b7280", command=self.clear_fields)
        self.clear_btn.grid(row=0, column=1, sticky="ew", padx=(6,0))

        # --- STATUS ---
        self.status = ctk.CTkLabel(frm, text="", wraplength=460, justify="left")
        self.status.grid(row=8, column=0, columnspan=2, sticky="ew", padx=12, pady=(10,12))

    # --- HELPERS ---
    def toggle_uri(self):
        use = self.use_uri.get() == 1
        self.uri_entry.configure(state="normal" if use else "disabled")
        for w in (self.host_entry, self.port_entry, self.user_entry, self.pass_entry, self.db_entry, self.tls_chk):
            w.configure(state="disabled" if use else "normal")

    def clear_fields(self):
        for w in (self.uri_entry, self.host_entry, self.port_entry, self.user_entry, self.pass_entry, self.db_entry):
            w.delete(0, "end")
        self.tls_chk.deselect()
        self.status.configure(text="")

    def build_uri_from_fields(self):
        host = self.host_entry.get().strip() or "localhost"
        port = self.port_entry.get().strip() or "27017"
        user = self.user_entry.get().strip()
        pwd  = self.pass_entry.get().strip()
        db   = self.db_entry.get().strip() or "admin"

        if user and pwd:
            user_e = urllib.parse.quote_plus(user)
            pwd_e  = urllib.parse.quote_plus(pwd)
            auth = f"{user_e}:{pwd_e}@"
        else:
            auth = ""

        return f"mongodb://{auth}{host}:{port}/{db}"

    def test_connection(self):
        self.status.configure(text="Connecting…")
        self.update_idletasks()

        try:
            if self.use_uri.get() == 1:
                uri = self.uri_entry.get().strip()
                if not uri:
                    self.status.configure(text="⚠️ URI vide.")
                    return
                client = MongoClient(uri, serverSelectionTimeoutMS=4000)
            else:
                uri = self.build_uri_from_fields()
                client = MongoClient(
                    uri,
                    tls=bool(self.tls_chk.get()),
                    serverSelectionTimeoutMS=4000
                )

            # Ping (depuis MongoDB 4.2+, ping sur admin)
            client.admin.command("ping")
            dbname = (client.get_database().name if client.get_database() is not None else "admin")
            self.status.configure(text=f"✅ Connection successful. URI: {mask_uri(uri)}  • DB: {dbname}")
            client.close()
        except PyMongoError as e:
            self.status.configure(text=f"❌ Connection failed: {e.__class__.__name__}: {e}")

def mask_uri(uri: str) -> str:
    # masque le mot de passe dans l'URI pour l'affichage
    try:
        if "@" in uri and "://" in uri:
            scheme, rest = uri.split("://", 1)
            creds, host = rest.split("@", 1)
            if ":" in creds:
                user, _pwd = creds.split(":", 1)
                return f"{scheme}://{user}:****@{host}"
    except Exception:
        pass
    return uri

if __name__ == "__main__":
    app = MongoApp()
    app.mainloop()
