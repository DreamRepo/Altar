import customtkinter as ctk
from pymongo.errors import PyMongoError, ConfigurationError
from services.mongo_conn import mongo_client_from_inputs, ping_and_get_dbname
from utils.uri import mask_uri


class MongoSection(ctk.CTkFrame):
    def __init__(self, master, on_save=None, on_change=None):
        super().__init__(master, corner_radius=12)
        self.on_save = on_save
        self.on_change = on_change

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self, text="MongoDB Connection", font=("Segoe UI", 18, "bold")).grid(
            row=0, column=0, columnspan=2, pady=(12, 12), sticky="w", padx=12
        )

        self.use_uri = ctk.CTkCheckBox(
            self, text="Use a MongoDB URI (mongodb:// or mongodb+srv://)", command=self.toggle_uri
        )
        self.use_uri.grid(row=1, column=0, columnspan=2, sticky="w", padx=12, pady=(0, 8))

        ctk.CTkLabel(self, text="URI").grid(row=2, column=0, columnspan=2, sticky="w", padx=12)
        self.uri_entry = ctk.CTkEntry(self, placeholder_text="mongodb://localhost:27017")
        self.uri_entry.grid(row=3, column=0, columnspan=2, sticky="ew", padx=12, pady=(0, 6))
        self.uri_entry.configure(state="disabled")

        ctk.CTkLabel(self, text="Host").grid(row=4, column=0, sticky="w", padx=12)
        self.host_entry = ctk.CTkEntry(self, placeholder_text="e.g., localhost")
        ctk.CTkLabel(self, text="Port").grid(row=4, column=1, sticky="w", padx=(6, 12))
        self.port_entry = ctk.CTkEntry(self, placeholder_text="27017")
        ctk.CTkLabel(self, text="Username").grid(row=6, column=0, sticky="w", padx=12)
        self.user_entry = ctk.CTkEntry(self, placeholder_text="optional")
        ctk.CTkLabel(self, text="Password").grid(row=6, column=1, sticky="w", padx=(6, 12))
        self.pass_entry = ctk.CTkEntry(self, placeholder_text="optional", show="•")
        ctk.CTkLabel(self, text="Database").grid(row=8, column=0, sticky="w", padx=12)
        self.db_entry = ctk.CTkEntry(self, placeholder_text="e.g., sacred")
        ctk.CTkLabel(self, text="Auth Source").grid(row=8, column=1, sticky="w", padx=(6, 12))
        self.auth_source_entry = ctk.CTkEntry(self, placeholder_text="e.g., admin")

        self.host_entry.grid(row=5, column=0, sticky="ew", padx=(12, 6), pady=(0, 4))
        self.port_entry.grid(row=5, column=1, sticky="ew", padx=(6, 12), pady=(0, 4))
        self.user_entry.grid(row=7, column=0, sticky="ew", padx=(12, 6), pady=(0, 4))
        self.pass_entry.grid(row=7, column=1, sticky="ew", padx=(6, 12), pady=(0, 4))
        self.db_entry.grid(row=9, column=0, sticky="ew", padx=(12, 6), pady=(0, 6))
        self.auth_source_entry.grid(row=9, column=1, sticky="ew", padx=(6, 12), pady=(0, 6))

        self.tls_chk = ctk.CTkCheckBox(self, text="TLS/SSL")
        self.tls_chk.grid(row=10, column=0, sticky="w", padx=12, pady=6)

        self.remember_pwd = ctk.CTkCheckBox(self, text="Save password")
        self.remember_pwd.grid(row=10, column=1, sticky="e", padx=12, pady=6)

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=11, column=0, columnspan=2, sticky="ew", padx=12, pady=(12, 4))
        btn_row.grid_columnconfigure((0, 1, 2), weight=1)

        self.test_btn = ctk.CTkButton(btn_row, text="Test connection", command=self.test_connection)
        self.test_btn.grid(row=0, column=0, sticky="ew", padx=(0, 6))

        self.save_btn = ctk.CTkButton(btn_row, text="Save settings", command=self._save)
        self.save_btn.grid(row=0, column=1, sticky="ew", padx=6)

        self.clear_btn = ctk.CTkButton(
            btn_row, text="Clear", fg_color="gray", hover_color="#6b7280", command=self.clear_fields
        )
        self.clear_btn.grid(row=0, column=2, sticky="ew", padx=(6, 0))

        self.status = ctk.CTkLabel(self, text="", wraplength=420, justify="left")
        self.status.grid(row=12, column=0, columnspan=2, sticky="ew", padx=12, pady=(10, 12))

    # --- Events / Actions ---
    def _save(self):
        if callable(self.on_save):
            self.on_save()
        if callable(self.on_change):
            self.on_change()

    def toggle_uri(self):
        use = self.use_uri.get() == 1
        self.uri_entry.configure(state="normal" if use else "disabled")
        for w in (self.host_entry, self.port_entry, self.user_entry, self.pass_entry, self.db_entry, self.auth_source_entry, self.tls_chk):
            w.configure(state="disabled" if use else "normal")
        if callable(self.on_change):
            self.on_change()

    def clear_fields(self):
        for w in (
            self.uri_entry,
            self.host_entry,
            self.port_entry,
            self.user_entry,
            self.pass_entry,
            self.db_entry,
            self.auth_source_entry,
        ):
            w.delete(0, "end")
        self.tls_chk.deselect()
        self.remember_pwd.deselect()
        self.status.configure(text="")
        if callable(self.on_change):
            self.on_change()

    def test_connection(self):
        self.status.configure(text="Connecting…")
        self.update_idletasks()
        try:
            client = mongo_client_from_inputs(
                use_uri=bool(self.use_uri.get()),
                uri=self.uri_entry.get().strip(),
                host=self.host_entry.get().strip(),
                port=self.port_entry.get().strip(),
                user=self.user_entry.get().strip(),
                pwd=self.pass_entry.get(),
                db=self.db_entry.get().strip(),
                auth_source=self.auth_source_entry.get().strip(),
                tls=bool(self.tls_chk.get()),
            )
            dbname = ping_and_get_dbname(client)
            self.status.configure(
                text=f"✅ Connection successful. URI: {mask_uri(client.address_string)}  • DB: {dbname}"
            )
            client.close()
            # propagate save request
            self._save()
        except ConfigurationError as e:
            self.status.configure(text=f"⚠️ Invalid configuration: {e}")
        except PyMongoError as e:
            self.status.configure(text=f"❌ Connection failed: {e.__class__.__name__}: {e}")
        except Exception as e:
            self.status.configure(text=f"❌ Error: {e.__class__.__name__}: {e}")
        if callable(self.on_change):
            self.on_change()

    # --- Prefs IO ---
    def get_prefs(self) -> dict:
        return {
            "use_uri": int(self.use_uri.get() == 1),
            "uri": self.uri_entry.get().strip(),
            "host": self.host_entry.get().strip(),
            "port": self.port_entry.get().strip(),
            "user": self.user_entry.get().strip(),
            "db": self.db_entry.get().strip(),
            "auth_source": self.auth_source_entry.get().strip(),
            "tls": int(self.tls_chk.get() == 1),
            "remember_pwd": int(self.remember_pwd.get() == 1),
        }

    def set_prefs(self, data: dict, password_loader=None):
        if data.get("use_uri"):
            self.use_uri.select()
        else:
            self.use_uri.deselect()
        self.toggle_uri()

        self.uri_entry.delete(0, "end"); self.uri_entry.insert(0, data.get("uri", ""))
        self.host_entry.delete(0, "end"); self.host_entry.insert(0, data.get("host", ""))
        self.port_entry.delete(0, "end"); self.port_entry.insert(0, data.get("port", ""))
        self.user_entry.delete(0, "end"); self.user_entry.insert(0, data.get("user", ""))
        self.db_entry.delete(0, "end");   self.db_entry.insert(0, data.get("db", ""))
        self.auth_source_entry.delete(0, "end"); self.auth_source_entry.insert(0, data.get("auth_source", ""))

        if data.get("tls"): self.tls_chk.select()
        else: self.tls_chk.deselect()

        if data.get("remember_pwd"): self.remember_pwd.select()
        else: self.remember_pwd.deselect()

        if callable(password_loader) and data.get("remember_pwd"):
            pwd = password_loader(user=data.get("user") or "default")
            if pwd:
                self.pass_entry.delete(0, "end")
                self.pass_entry.insert(0, pwd)

    def get_password(self) -> str:
        return self.pass_entry.get()

