"""Main application GUI using CustomTkinter."""
import customtkinter as ctk
from tkinter import messagebox
import webbrowser
import threading
import sys

# Support both package imports (tests, python -m) and direct script runs
try:
    from .mongodb import MongoDBClient
    from .omniboard import OmniboardManager
    from .prefs import Preferences
except ImportError:
    from mongodb import MongoDBClient
    from omniboard import OmniboardManager
    from prefs import Preferences

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")


class MongoApp(ctk.CTk):
    """Main application window for MongoDB Database Selector (AltarViewer)."""
    
    def __init__(self):
        """Initialize the main application window."""
        super().__init__()
        self.title("MongoDB Database Selector")
        self.geometry("550x700")
        self.resizable(False, False)
        
        # Hide window initially to allow background loading
        self.withdraw()

        # Initialize backend managers
        self.mongo_client = MongoDBClient()
        self.omniboard_manager = OmniboardManager()
        self.preferences = Preferences()

        # UI state variables
        self.port_var = ctk.StringVar(value="27017")
        self.mongo_url_var = ctk.StringVar(value="mongodb://localhost:27017/")
        self.connection_mode = ctk.StringVar(value="Port")
        self.db_list = []
        self.selected_db = ctk.StringVar()

        # Configure grid weight
        self.grid_columnconfigure(0, weight=1)

        # Initialize UI components
        self._create_title()
        self._create_connection_frame()
        self._create_database_frame()
        self._create_omniboard_frame()
        # Load saved preferences (best-effort)
        try:
            self._load_prefs_and_apply()
        except Exception:
            pass
        # Track last mode to persist prefs on mode switches
        self._last_mode = self.connection_mode.get()
        
        # Show window after 2 second delay
        self.after(2000, self.deiconify)

    def _create_title(self):
        """Create the title label."""
        title_label = ctk.CTkLabel(
            self, 
            text="AltarViewer",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="ew")

    def _create_connection_frame(self):
        """Create the connection configuration frame."""
        self.connection_frame = ctk.CTkFrame(self)
        self.connection_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        self.connection_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            self.connection_frame, 
            text="Connect to MongoDB",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(5, 2), sticky="w")

        # Connection mode selector
        self.mode_selector = ctk.CTkSegmentedButton(
            self.connection_frame,
            values=["Port", "Full URI", "Credential URI"],
            variable=self.connection_mode,
            command=self.on_connection_mode_change
        )
        self.mode_selector.grid(row=1, column=0, columnspan=2, padx=10, pady=2, sticky="ew")

        # Port entry
        self.port_label = ctk.CTkLabel(self.connection_frame, text="Port:")
        self.port_label.grid(row=2, column=0, padx=(10, 5), pady=5, sticky="w")
        self.port_entry = ctk.CTkEntry(
            self.connection_frame, 
            textvariable=self.port_var,
            width=100,
            placeholder_text="27017"
        )
        self.port_entry.grid(row=2, column=1, padx=(5, 10), pady=5, sticky="w")

        # MongoDB URI entry (initially hidden)
        self.url_label = ctk.CTkLabel(self.connection_frame, text="MongoDB URI:")
        self.url_entry = ctk.CTkEntry(
            self.connection_frame,
            textvariable=self.mongo_url_var,
            placeholder_text="mongodb://localhost:27017/",
            width=300
        )
        # Warning label for credentials in URI (initially hidden)
        self.url_warning_label = ctk.CTkLabel(
            self.connection_frame,
            text="do not paste password here, use credential URI tab instead",
            text_color="#cc9900",
            font=ctk.CTkFont(size=11),
            anchor="w",
            wraplength=380,
            justify="left",
        )
        self.url_label.grid_remove()
        self.url_entry.grid_remove()
        self.url_warning_label.grid_remove()

        # Credential URI mode widgets (initially hidden)
        self.cred_uri_label = ctk.CTkLabel(self.connection_frame, text="Credential-less MongoDB URI:")
        self.cred_uri_entry = ctk.CTkEntry(
            self.connection_frame,
            placeholder_text="mongodb://host:27017/yourdb?options",
            width=300,
        )
        self.cred_user_label = ctk.CTkLabel(self.connection_frame, text="Username:")
        self.cred_user_entry = ctk.CTkEntry(
            self.connection_frame,
            placeholder_text="username",
            width=150,
        )
        self.cred_pass_label = ctk.CTkLabel(self.connection_frame, text="Password:")
        self.cred_pass_entry = ctk.CTkEntry(
            self.connection_frame,
            placeholder_text="password",
            show="•",
            width=150,
        )
        self.cred_authsrc_label = ctk.CTkLabel(self.connection_frame, text="Auth Source:")
        self.cred_authsrc_entry = ctk.CTkEntry(
            self.connection_frame,
            placeholder_text="admin (optional)",
            width=150,
        )
        # Remember password (secure keyring) checkbox (only for Credential URI mode)
        self.remember_pwd_chk = ctk.CTkCheckBox(
            self.connection_frame,
            text="Save password securely (OS keyring)",
            command=self.on_remember_toggle,
        )
        # Hide initially
        for w in (
            self.cred_uri_label, self.cred_uri_entry,
            self.cred_user_label, self.cred_user_entry,
            self.cred_pass_label, self.cred_pass_entry,
            self.cred_authsrc_label, self.cred_authsrc_entry,
            self.remember_pwd_chk,
        ):
            w.grid_remove()

        # Connect button
        self.connect_btn = ctk.CTkButton(
            self.connection_frame,
            text="Connect to MongoDB",
            command=self.connect,
            height=28,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        # Place connect button; will be dynamically re-positioned per mode
        self.connect_btn.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

    def _create_database_frame(self):
        """Create the database selection frame."""
        self.db_frame = ctk.CTkFrame(self)
        self.db_frame.grid(row=2, column=0, padx=20, pady=5, sticky="nsew")
        self.db_frame.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            self.db_frame,
            text="Available Databases",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, padx=10, pady=(5, 2), sticky="w")

        # Scrollable frame for databases
        self.db_scrollable_frame = ctk.CTkScrollableFrame(
            self.db_frame, 
            height=300, 
            fg_color=("gray95", "gray20")
        )
        self.db_scrollable_frame.grid(row=1, column=0, padx=10, pady=2, sticky="nsew")
        self.db_frame.grid_rowconfigure(1, weight=1)
        
        self.db_labels = []
        self.selected_db_label = None

        # Selected database label
        self.selected_label = ctk.CTkLabel(
            self.db_frame,
            text="No database selected",
            font=ctk.CTkFont(size=12),
            text_color="gray70"
        )
        self.selected_label.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

    def _create_omniboard_frame(self):
        """Create the Omniboard control frame."""
        self.omniboard_frame = ctk.CTkFrame(self)
        self.omniboard_frame.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        self.omniboard_frame.grid_columnconfigure(0, weight=1)

        # Launch Omniboard button
        self.launch_btn = ctk.CTkButton(
            self.omniboard_frame,
            text="Launch Omniboard",
            command=self.launch_omniboard,
            state="disabled",
            height=32,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#1f6aa5",
            hover_color="#144870"
        )
        self.launch_btn.grid(row=0, column=0, padx=10, pady=(5, 3), sticky="ew")

        # Clear Docker containers button
        self.clear_docker_btn = ctk.CTkButton(
            self.omniboard_frame,
            text="Clear All Omniboard Containers",
            command=self.clear_omniboard_docker,
            height=28,
            font=ctk.CTkFont(size=12),
            fg_color="#8B0000",
            hover_color="#660000"
        )
        self.clear_docker_btn.grid(row=1, column=0, padx=10, pady=3, sticky="ew")

        # Label for Omniboard URLs
        ctk.CTkLabel(
            self.omniboard_frame,
            text="Omniboard URLs:",
            font=ctk.CTkFont(size=11, weight="bold"),
            anchor="w"
        ).grid(row=2, column=0, padx=10, pady=(5, 0), sticky="w")

        # Omniboard info textbox (for clickable links)
        self.omniboard_info_text = ctk.CTkTextbox(
            self.omniboard_frame,
            height=80,
            wrap="word",
            font=ctk.CTkFont(size=11)
        )
        self.omniboard_info_text.grid(row=3, column=0, padx=10, pady=(2, 5), sticky="ew")
        self.omniboard_info_text.configure(state="disabled")
        
        # Configure link tag for blue, underlined, clickable text
        self.omniboard_info_text.tag_config("link", foreground="#1f6aa5", underline=True)
        self.omniboard_info_text.tag_bind("link", "<Button-1>", self.on_link_click)
        self.omniboard_info_text.tag_bind("link", "<Enter>", 
                                          lambda e: self.omniboard_info_text.configure(cursor="hand2"))
        self.omniboard_info_text.tag_bind("link", "<Leave>", 
                                          lambda e: self.omniboard_info_text.configure(cursor=""))

    def on_connection_mode_change(self, value):
        """Toggle between Port and Full URI input modes."""
        # If leaving Credential URI mode, persist current preferences (and keyring if opted-in)
        try:
            if getattr(self, "_last_mode", None) == "Credential URI":
                self._save_prefs(remember_pwd=bool(self.remember_pwd_chk.get()))
        except Exception:
            pass
        if value == "Port":
            self.port_label.grid(row=2, column=0, padx=(10, 5), pady=5, sticky="w")
            self.port_entry.grid(row=2, column=1, padx=(5, 10), pady=5, sticky="w")
            self.url_label.grid_remove()
            self.url_entry.grid_remove()
            self.url_warning_label.grid_remove()
            # Hide credential URI widgets
            for w in (
                self.cred_uri_label, self.cred_uri_entry,
                self.cred_user_label, self.cred_user_entry,
                self.cred_pass_label, self.cred_pass_entry,
                self.cred_authsrc_label, self.cred_authsrc_entry,
                self.remember_pwd_chk,
            ):
                w.grid_remove()
            # Connect button row for this mode
            self.connect_btn.grid_configure(row=4)
        elif value == "Full URI":
            self.port_label.grid_remove()
            self.port_entry.grid_remove()
            self.url_label.grid(row=2, column=0, padx=(10, 5), pady=5, sticky="w")
            self.url_entry.grid(row=2, column=1, padx=(5, 10), pady=5, sticky="ew")
            # Show the warning below the URI input
            self.url_warning_label.grid(row=3, column=0, columnspan=2, padx=(10, 10), pady=(0, 4), sticky="w")
            # Hide credential URI widgets
            for w in (
                self.cred_uri_label, self.cred_uri_entry,
                self.cred_user_label, self.cred_user_entry,
                self.cred_pass_label, self.cred_pass_entry,
                self.cred_authsrc_label, self.cred_authsrc_entry,
                self.remember_pwd_chk,
            ):
                w.grid_remove()
            # Connect button row for this mode
            self.connect_btn.grid_configure(row=4)
        else:  # Credential URI
            # Hide port and full URI widgets
            self.port_label.grid_remove()
            self.port_entry.grid_remove()
            self.url_label.grid_remove()
            self.url_entry.grid_remove()
            self.url_warning_label.grid_remove()
            # Show credential-less URI row
            self.cred_uri_label.grid(row=2, column=0, padx=(10, 5), pady=5, sticky="w")
            self.cred_uri_entry.grid(row=2, column=1, padx=(5, 10), pady=5, sticky="ew")
            # Show username/password/authSource rows
            self.cred_user_label.grid(row=3, column=0, padx=(10, 5), pady=2, sticky="w")
            self.cred_user_entry.grid(row=3, column=1, padx=(5, 10), pady=2, sticky="w")
            self.cred_pass_label.grid(row=4, column=0, padx=(10, 5), pady=2, sticky="w")
            self.cred_pass_entry.grid(row=4, column=1, padx=(5, 10), pady=2, sticky="w")
            self.cred_authsrc_label.grid(row=5, column=0, padx=(10, 5), pady=2, sticky="w")
            self.cred_authsrc_entry.grid(row=5, column=1, padx=(5, 10), pady=2, sticky="w")
            self.remember_pwd_chk.grid(row=6, column=0, columnspan=2, padx=(10, 10), pady=(4, 4), sticky="w")
            # Place connect button below these rows
            self.connect_btn.grid_configure(row=7)
            # Auto-fill password from keyring if we have a remembered one and the field is empty
            try:
                self._auto_fill_credential_password_if_needed()
            except Exception:
                pass
        # Update last mode
        self._last_mode = value

    def connect(self):
        """Connect to MongoDB and list available databases."""
        # Clear previous database labels
        for label in self.db_labels:
            label.destroy()
        self.db_labels.clear()
        self.selected_db_label = None
        
        self.selected_label.configure(text="Connecting...")
        
        try:
            # Connect based on mode
            mode = self.connection_mode.get()
            if mode == "Port":
                port = self.port_var.get() or "27017"
                dbs = self.mongo_client.connect_by_port(port)
            elif mode == "Full URI":
                url = self.mongo_url_var.get().strip()
                if not url:
                    messagebox.showerror("Error", "Please provide a valid MongoDB URI.")
                    self.selected_label.configure(text="Connection failed")
                    return
                dbs = self.mongo_client.connect_by_url(url)
            else:  # Credential URI
                base_uri = self.cred_uri_entry.get().strip()
                user = self.cred_user_entry.get().strip()
                pwd = self.cred_pass_entry.get()
                auth_src = self.cred_authsrc_entry.get().strip()
                if not base_uri:
                    messagebox.showerror("Error", "Please provide a credential-less MongoDB URI.")
                    self.selected_label.configure(text="Connection failed")
                    return
                # Ensure scheme
                if not base_uri.startswith("mongodb://") and not base_uri.startswith("mongodb+srv://"):
                    base_uri = "mongodb://" + base_uri
                # Build a temporary URI for connecting (do not display it)
                from urllib.parse import urlparse, urlunparse, quote_plus
                parsed = urlparse(base_uri)
                # Inject userinfo if provided
                userinfo = ""
                if user:
                    userinfo += quote_plus(user)
                    if pwd:
                        userinfo += f":{quote_plus(pwd)}"
                    userinfo += "@"
                host = parsed.hostname or "localhost"
                port = f":{parsed.port}" if parsed.port else ""
                netloc = f"{userinfo}{host}{port}"
                query = parsed.query
                if auth_src and "authSource=" not in query:
                    sep = "&" if query else "?"
                    query = f"{query}{sep}authSource={auth_src}" if query else f"authSource={auth_src}"
                temp_uri = urlunparse((parsed.scheme, netloc, parsed.path, "", query, ""))
                dbs = self.mongo_client.connect_by_url(temp_uri)
                # Save preferences (including secure password via keyring if opted-in)
                try:
                    self._save_prefs(remember_pwd=bool(self.remember_pwd_chk.get()))
                except Exception:
                    pass
            if mode != "Credential URI":
                # Save non-secret prefs for other modes
                try:
                    self._save_prefs(remember_pwd=False)
                except Exception:
                    pass
            
            self.db_list = dbs
            
            if not dbs:
                self.selected_label.configure(text="No databases found")
                no_db_label = ctk.CTkLabel(
                    self.db_scrollable_frame,
                    text="No databases found",
                    text_color="gray60"
                )
                no_db_label.pack(pady=10)
                self.db_labels.append(no_db_label)
            else:
                for db in dbs:
                    label = ctk.CTkLabel(
                        self.db_scrollable_frame,
                        text=db,
                        height=22,
                        font=ctk.CTkFont(size=13),
                        cursor="hand2",
                        anchor="w",
                        padx=10,
                        fg_color="transparent"
                    )
                    label.pack(pady=0, padx=5, fill="x")
                    label.bind("<Button-1>", lambda e, d=db: self.select_database(d))
                    label.bind("<Enter>", lambda e, l=label: l.configure(fg_color=("gray85", "gray30")))
                    label.bind("<Leave>", lambda e, l=label: l.configure(fg_color="transparent") 
                              if l != self.selected_db_label else None)
                    self.db_labels.append(label)
                
                self.selected_label.configure(text="Please select a database")
        except Exception as e:
            error_msg = str(e)
            
            # Provide friendlier error messages
            if "ServerSelectionTimeoutError" in error_msg or "timed out" in error_msg.lower():
                friendly_msg = (
                    "Cannot connect to MongoDB server.\n\n"
                    "Please ensure:\n"
                    "• MongoDB is running on the specified port\n"
                    "• The port number is correct\n"
                    "• Your firewall allows the connection"
                )
            elif "connection refused" in error_msg.lower():
                friendly_msg = (
                    "Connection refused by MongoDB server.\n\n"
                    "MongoDB may not be running on this port.\n"
                    "Please start MongoDB or verify the port number."
                )
            elif "authentication failed" in error_msg.lower():
                friendly_msg = (
                    "MongoDB authentication failed.\n\n"
                    "Please check your username and password in the connection URL."
                )
            elif "dnspython" in error_msg.lower() or ("mongodb+srv" in error_msg.lower() and "dns" in error_msg.lower()):
                friendly_msg = (
                    "SRV connection detected but 'dnspython' is not installed.\n\n"
                    "To use URIs starting with 'mongodb+srv://', please install dnspython:\n"
                    "pip install dnspython\n\n"
                    "Alternatively, use a standard 'mongodb://' URI with explicit host and port."
                )
            else:
                friendly_msg = f"Connection Error:\n\n{error_msg}"
            
            messagebox.showerror("MongoDB Connection Failed", friendly_msg)
            self.selected_label.configure(text="Connection failed")

    def select_database(self, db_name):
        """Select a database and enable the launch button."""
        self.selected_db.set(db_name)
        self.selected_label.configure(
            text=f"Selected: {db_name}",
            text_color=("#1f6aa5", "#5fb4ff")
        )
        self.launch_btn.configure(state="normal")
        
        # Update label appearance to show selection
        for label in self.db_labels:
            if isinstance(label, ctk.CTkLabel) and label.cget("text") == db_name:
                label.configure(fg_color=("#1f6aa5", "#1f6aa5"), text_color="white")
                self.selected_db_label = label
            elif isinstance(label, ctk.CTkLabel) and label.cget("text") != "No databases found":
                label.configure(fg_color="transparent", text_color=("black", "white"))

    def launch_omniboard(self):
        """Launch Omniboard in a Docker container for the selected database."""
        db_name = self.selected_db.get()
        if not db_name:
            messagebox.showerror("Error", "No database selected.")
            return
        # Gather connection details once on UI thread
        mongo_host, mongo_port, _ = self.mongo_client.parse_connection_url()
        mongo_uri = None
        mode = self.connection_mode.get()
        if mode == "Full URI":
            if hasattr(self.mongo_client, "get_connection_uri"):
                mongo_uri = self.mongo_client.get_connection_uri()
        elif mode == "Credential URI":
            if hasattr(self.mongo_client, "get_connection_uri"):
                mongo_uri = self.mongo_client.get_connection_uri()

        # Require Docker to be running; no auto-start
        if not self.omniboard_manager.is_docker_running():
            messagebox.showinfo(
                "Docker not running",
                "Docker Desktop is not running. Please launch Docker Desktop manually, "
                "wait until it is ready, and then click 'Launch Omniboard' again.",
            )
            return

        # Docker is already running; launch in background
        self._launch_container_async(db_name, mongo_host, mongo_port, mongo_uri)

    def _launch_container_async(self, db_name: str, mongo_host: str, mongo_port: int, mongo_uri: str | None):
        """Run container launch in a worker thread and update UI on completion."""
        def worker():
            try:
                container_name, host_port = self.omniboard_manager.launch(
                    db_name=db_name,
                    mongo_host=mongo_host,
                    mongo_port=mongo_port,
                    mongo_uri=mongo_uri,
                )
                url = f"http://localhost:{host_port}"
                self.after(0, lambda: self._on_omniboard_launched(db_name, url))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Launch Error", str(e)))

        self.selected_label.configure(text=f"Launching Omniboard for '{db_name}'…")
        self.launch_btn.configure(state="disabled")
        threading.Thread(target=worker, daemon=True).start()

    def _on_omniboard_launched(self, db_name: str, url: str):
        # Update textbox with clickable link
        self.omniboard_info_text.configure(state="normal")
        text_before = f"Omniboard for '{db_name}': "
        self.omniboard_info_text.insert("end", text_before)

        # Insert URL as a clickable link
        url_start = self.omniboard_info_text.index("end-1c")
        self.omniboard_info_text.insert("end", url)
        url_end = self.omniboard_info_text.index("end-1c")

        # Apply tags
        self.omniboard_info_text.tag_add("link", url_start, url_end)
        self.omniboard_info_text.tag_add(f"url_{url}", url_start, url_end)

        self.omniboard_info_text.insert("end", "\n")
        self.omniboard_info_text.configure(state="disabled")
        self.launch_btn.configure(state="normal")

        # Open in browser after a short delay to allow Omniboard to fully start
        self.after(6000, lambda: webbrowser.open(url))

    def _auto_fill_credential_password_if_needed(self):
        """If remember is enabled and password field is empty, load from keyring."""
        if not hasattr(self, "preferences"):
            return
        data = self.preferences.load()
        remember = int(data.get("remember_pwd", 0)) == 1 or int(self.remember_pwd_chk.get()) == 1
        if not remember:
            return
        # Prefer current UI username, else stored one
        user = self.cred_user_entry.get().strip() or data.get("user") or "default"
        if not self.cred_pass_entry.get().strip():
            pwd = self.preferences.load_password_if_any(user)
            if pwd:
                self.cred_pass_entry.delete(0, "end")
                self.cred_pass_entry.insert(0, pwd)
                # Ensure checkbox reflects remembered state
                if int(self.remember_pwd_chk.get()) != 1:
                    self.remember_pwd_chk.select()

    def on_remember_toggle(self):
        """Handle toggling of the remember password checkbox."""
        if self.connection_mode.get() != "Credential URI":
            return
        if not hasattr(self, "preferences"):
            return
        # Check keyring availability
        if not self.preferences.is_keyring_available():
            messagebox.showinfo(
                "Keyring not available",
                "Password storage requires the 'keyring' package and an OS-supported keychain.\n"
                "Please install dependencies (pip install keyring) or disable this option.",
            )
            self.remember_pwd_chk.deselect()
            return
        # If enabling, immediately save current password (if any)
        if int(self.remember_pwd_chk.get()) == 1:
            user = (self.cred_user_entry.get().strip() or "default")
            pwd = self.cred_pass_entry.get()
            try:
                self.preferences.save_password_if_allowed(True, user, pwd)
                # Persist non-secret prefs too
                self._save_prefs(remember_pwd=True)
            except Exception:
                # If saving fails, uncheck it
                self.remember_pwd_chk.deselect()
        else:
            # If disabling, remove stored password
            user = (self.cred_user_entry.get().strip() or "default")
            try:
                self.preferences.save_password_if_allowed(False, user, "")
                self._save_prefs(remember_pwd=False)
            except Exception:
                pass

    def _load_prefs_and_apply(self):
        """Load saved preferences and apply to the UI."""
        data = self.preferences.load()
        if not isinstance(data, dict) or not data:
            return
        mode = data.get("mode") or "Port"
        # Set mode and update UI
        self.connection_mode.set(mode)
        self.on_connection_mode_change(mode)
        if mode == "Port":
            if data.get("port"):
                self.port_var.set(str(data.get("port")))
        elif mode == "Full URI":
            # Do not load/persist the Full URI value for security/privacy
            # Leave the default placeholder as-is
            pass
        elif mode == "Credential URI":
            self.cred_uri_entry.delete(0, "end"); self.cred_uri_entry.insert(0, data.get("cred_uri", ""))
            self.cred_user_entry.delete(0, "end"); self.cred_user_entry.insert(0, data.get("user", ""))
            self.cred_authsrc_entry.delete(0, "end"); self.cred_authsrc_entry.insert(0, data.get("auth_source", ""))
            if int(data.get("remember_pwd", 0)) == 1:
                self.remember_pwd_chk.select()
                pwd = self.preferences.load_password_if_any(data.get("user") or "default")
                if pwd:
                    self.cred_pass_entry.delete(0, "end")
                    self.cred_pass_entry.insert(0, pwd)

    def _save_prefs(self, remember_pwd: bool):
        """Save current preferences. Password stored in OS keyring if requested."""
        mode = self.connection_mode.get()
        data = {"mode": mode}
        if mode == "Port":
            data.update({"port": self.port_var.get().strip()})
        elif mode == "Full URI":
            # Intentionally do not persist the Full URI
            pass
        elif mode == "Credential URI":
            user = (self.cred_user_entry.get().strip() or "default")
            pwd = self.cred_pass_entry.get()
            data.update({
                "cred_uri": self.cred_uri_entry.get().strip(),
                "user": user,
                "auth_source": self.cred_authsrc_entry.get().strip(),
                "remember_pwd": 1 if remember_pwd else 0,
            })
            self.preferences.save_password_if_allowed(remember_pwd, user, pwd)
        self.preferences.save_without_password(data)

    def clear_omniboard_docker(self):
        """Remove all Omniboard Docker containers."""
        try:
            count = self.omniboard_manager.clear_all_containers()
            
            if count == 0:
                messagebox.showinfo("Docker", "No Omniboard containers to remove.")
            else:
                messagebox.showinfo("Docker", f"Removed {count} Omniboard container(s).")
            
            # Clear the info textbox
            self.omniboard_info_text.configure(state="normal")
            self.omniboard_info_text.delete("1.0", "end")
            self.omniboard_info_text.configure(state="disabled")
        except Exception as e:
            messagebox.showerror("Docker Error", str(e))

    def on_link_click(self, event):
        """Handle clicks on hyperlinks in the textbox."""
        try:
            index = self.omniboard_info_text.index(f"@{event.x},{event.y}")
            tags = self.omniboard_info_text.tag_names(index)
            
            for tag in tags:
                if tag.startswith('url_'):
                    url = tag[4:]
                    webbrowser.open(url)
                    break
        except Exception:
            pass
