import customtkinter as ctk
from services.prefs import Preferences
from services.experiment_sender import send_experiment
from pathlib import Path
from ui.mongo_view import MongoSection
from ui.minio_view import MinioSection
from ui.experiment_view import ExperimentSection
from utils.error_dialog import show_error, format_error_message, log_error
import threading


class AppView(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AltarSender")
        # Window size will adapt to content via fit_to_content()
        # Start wider by default
        self.geometry("1200x800")

        # Prefs (sauvegarde/restauration)
        self.prefs = Preferences()

        # --- ROOT GRID ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SCROLLABLE FRAME ---
        frm = ctk.CTkScrollableFrame(self, corner_radius=12, height=700, fg_color="transparent")
        frm.grid(row=0, column=0, padx=16, pady=16, sticky="nsew")
        # keep a reference to adjust height dynamically on resize
        self.content_frame = frm
        frm.grid_columnconfigure(0, weight=1)
        frm.grid_columnconfigure(1, weight=2)

        # Left stack: Mongo (top) then MinIO (bottom)
        self.mongo_section = MongoSection(frm, on_save=self.save_prefs, on_change=lambda: self.after(10, self.fit_to_content))
        self.mongo_section.grid(row=0, column=0, sticky="nsew", padx=12, pady=(8, 8))

        # --- MINIO SECTION (below Mongo on the left) ---
        self.minio_section = MinioSection(frm, on_save=self.save_prefs, on_change=lambda: self.after(10, self.fit_to_content))
        self.minio_section.grid(row=1, column=0, sticky="nsew", padx=12, pady=(8, 8))

        # --- EXPERIMENT FILES SECTION ---
        self.exp_section = ExperimentSection(
            frm,
            on_change=self._on_experiment_change,
            on_send=self._on_send_experiment,
            on_minio_toggle=self._on_minio_toggle,
        )
        self.exp_section.grid(row=0, column=1, rowspan=20, sticky="nsew", padx=12, pady=(8, 8))

        # (button and status are now inside ExperimentSection)

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
        try:
            data = self.prefs.load()
            # delegate to sections
            self.mongo_section.set_prefs(data, password_loader=lambda user: self.prefs.load_password_if_any(user=user))
            self.exp_section.set_prefs(data)
            # ensure experiment cards render on launch
            self.exp_section.render_details_sections()
            self.minio_section.set_prefs(data, password_loader=lambda user: self.prefs.load_password_if_any(user=user))
            # Set initial MinIO section visibility based on send_minio setting
            self._on_minio_toggle(bool(data.get("raw_data_send_minio", 1)))
            self.after(10, self.fit_to_content)
        except Exception as e:
            log_error(e, "Error loading preferences")
            show_error(self, "Load Preferences Error", f"Could not load preferences: {e}", e)

    # --- Send experiment handler ---
    def _on_send_experiment(self):
        try:
            # persist current values first
            self.save_prefs()
        except Exception as e:
            log_error(e, "Error saving preferences before send")
        
        # Check if MinIO is required but not validated
        send_minio = self.exp_section._raw_data_settings.get("send_minio", False)
        raw_data_name = self.exp_section.file_menus.get("raw_data", None)
        has_raw_data = False
        if raw_data_name:
            val = (raw_data_name.get() or "").strip()
            has_raw_data = bool(val) and val != "None"
        
        if send_minio and has_raw_data:
            if not self.minio_section.is_connection_valid():
                error_msg = "MinIO connection not validated. Please test the MinIO connection before sending."
                self.exp_section.send_status.configure(text=f"❌ {error_msg}")
                show_error(self, "MinIO Connection Required", error_msg)
                return
        
        # aggregate data
        data = self.prefs_dict()
        # Build structured payload with selectors grouped under experiment
        payload = {
            "mongo": {
                "use_uri": data.get("use_uri", 0),
                "uri": data.get("uri", ""),
                "host": data.get("host", ""),
                "port": data.get("port", ""),
                "user": data.get("user", ""),
                "db": data.get("db", ""),
                "auth_source": data.get("auth_source", ""),
                "tls": data.get("tls", 0),
                "password": self.mongo_section.get_password(),
            },
            "minio": {
                "endpoint": data.get("minio_endpoint", ""),
                "access_key": data.get("minio_access_key", ""),
                "tls": data.get("minio_tls", 0),
                "secret_key": self.minio_section.get_secret(),
                "bucket": data.get("minio_bucket", ""),
            },
            "experiment": {
                "folder": data.get("experiment_folder", ""),
                "name": data.get("experiment_name", ""),
                "folders": data.get("experiment_folders", []),
                "selectors": {
                    "config": {
                        "name": data.get("config_name", ""),
                        "sheet": data.get("config_sheet", ""),
                        "use_custom_path": data.get("config_use_custom_path", 0),
                        "custom_path": data.get("config_custom_path", ""),
                        "options": {
                            "flatten": data.get("config_flatten", 0),
                            "sep": data.get("config_sep", ","),
                        },
                        "parse_from_folder": data.get("config_parse_from_folder", 0),
                        "folder_pattern": data.get("config_folder_pattern", ""),
                        "parsed_folder_values": data.get("config_parsed_folder_values", {}),
                    },
                    "metrics": {
                        "name": data.get("metrics_name", ""),
                        "sheet": data.get("metrics_sheet", ""),
                        "options": {
                            "header": data.get("metrics_header", 0),
                            "has_time": data.get("metrics_has_time", 0),
                            "time_col": data.get("metrics_time_col", ""),
                            "selected_cols": data.get("metrics_selected_cols", []),
                            "sep": data.get("metrics_sep", ","),
                        },
                    },
                    "results": {
                        "name": data.get("results_name", ""),
                        "sheet": data.get("results_sheet", ""),
                        "options": {
                            "sep": data.get("results_sep", ","),
                        },
                    },
                    "raw_data": {
                        "name": data.get("raw_data_name", ""),
                        "files": data.get("raw_data_files", []),
                        "options": {
                            "send_minio": data.get("raw_data_send_minio", 1),
                            "save_locally": data.get("raw_data_save_locally", 0),
                            "local_path": data.get("raw_data_local_path", ""),
                        },
                    },
                    "artifacts": {
                        "name": data.get("artifacts_name", ""),
                        "files": data.get("artifacts_files", []),
                    },
                },
            },
        }

        # produce payload and call service (non-blocking)
        try:
            self.exp_section.send_status.configure(text="Sending experiment…")
            # disable button to avoid double-clicks
            self.exp_section.send_btn.configure(state="disabled")

            def _worker():
                res = None
                err = None
                try:
                    res = send_experiment(payload)
                except Exception as e:
                    err = e
                    log_error(e, "Error in send_experiment")

                def _update_ui():
                    if err is not None:
                        error_msg = format_error_message(err)
                        self.exp_section.send_status.configure(text=error_msg)
                        # Show detailed error dialog
                        show_error(self, "Send Experiment Failed", str(err), err)
                    else:
                        if isinstance(res, dict) and res.get("ok"):
                            self.exp_section.send_status.configure(text=f"✅ {res.get('message', 'OK')}")
                        else:
                            msg = (res.get("message") if isinstance(res, dict) else str(res)) or "Failed"
                            self.exp_section.send_status.configure(text=f"❌ {msg}")
                    
                    self.exp_section.send_btn.configure(state="normal")
                    self.after(10, self.fit_to_content)

                self.after(0, _update_ui)

            threading.Thread(target=_worker, daemon=True).start()
        except Exception as e:
            log_error(e, "Error starting send thread")
            self.exp_section.send_status.configure(text=format_error_message(e))
            self.exp_section.send_btn.configure(state="normal")
            show_error(self, "Send Error", str(e), e)
        self.after(10, self.fit_to_content)

    def _on_experiment_change(self):
        """Handle experiment section changes and update MinIO visibility."""
        self._on_minio_toggle()
        self.after(0, self.fit_to_content)

    def _on_minio_toggle(self, send_minio: bool = None):
        """Show or hide the MinIO section based on send_minio setting and raw_data selection."""
        try:
            # Get current state from experiment section if not provided
            if send_minio is None:
                send_minio = self.exp_section._raw_data_settings.get("send_minio", True)
            
            # Check if raw_data is selected (not None or empty)
            raw_data_name = self.exp_section.file_menus.get("raw_data", None)
            has_raw_data = False
            if raw_data_name:
                val = (raw_data_name.get() or "").strip()
                has_raw_data = bool(val) and val != "None"
            
            # Show MinIO section only if both conditions are met
            if send_minio and has_raw_data:
                self.minio_section.grid()
            else:
                self.minio_section.grid_remove()
            self.after(10, self.fit_to_content)
        except Exception as e:
            log_error(e, "Error toggling MinIO section visibility")

    def on_close(self):
        # Sauvegarde avant sortie
        self.save_prefs()
        self.destroy()

    # --- Window sizing helper ---
    def fit_to_content(self):
        try:
            self.update_idletasks()
            req_w = self.winfo_reqwidth()
            req_h = self.winfo_reqheight()
            # widen default clamps
            min_w, max_w = 1200, 1800
            min_h, max_h = 800, 1000
            new_w = max(min(req_w, max_w), min_w)
            new_h = max(min(req_h, max_h), min_h)
            self.minsize(min_w, min_h)
            self.geometry(f"{new_w}x{new_h}")
            # adjust scrollable frame height so it doesn't reserve extra space
            self.content_frame.configure(height=max(min_h - 40, 400))
        except Exception as e:
            # Window sizing errors are non-critical, just log them
            log_error(e, "Error fitting window to content")

