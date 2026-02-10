import customtkinter as ctk
import urllib.request
import urllib.error


class MinioSection(ctk.CTkFrame):
    def __init__(self, master, on_save=None, on_change=None):
        super().__init__(master, corner_radius=12)
        self.on_save = on_save
        self.on_change = on_change
        # Track whether connection test passed
        self._connection_valid = False
        self._last_tested_config = None  # To detect config changes

        self.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(self, text="MinIO Connection", font=("Segoe UI", 18, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(12, 8)
        )

        ctk.CTkLabel(self, text="Endpoint (host[:port] or URL)").grid(row=1, column=0, sticky="w", padx=12)
        self.endpoint_entry = ctk.CTkEntry(self, placeholder_text="localhost:9000")
        self.endpoint_entry.grid(row=1, column=1, sticky="ew", padx=(6, 12), pady=6)

        ctk.CTkLabel(self, text="Access key").grid(row=2, column=0, sticky="w", padx=12)
        self.access_key_entry = ctk.CTkEntry(self, placeholder_text="minioadmin")
        self.access_key_entry.grid(row=2, column=1, sticky="ew", padx=(6, 12), pady=6)

        ctk.CTkLabel(self, text="Secret key").grid(row=3, column=0, sticky="w", padx=12)
        self.secret_entry = ctk.CTkEntry(self, placeholder_text="••••••••", show="•")
        self.secret_entry.grid(row=3, column=1, sticky="ew", padx=(6, 12), pady=6)

        ctk.CTkLabel(self, text="Bucket").grid(row=4, column=0, sticky="w", padx=12)
        self.bucket_entry = ctk.CTkEntry(self, placeholder_text="my-bucket")
        self.bucket_entry.grid(row=4, column=1, sticky="ew", padx=(6, 12), pady=6)

        self.tls_chk = ctk.CTkCheckBox(self, text="TLS/SSL")
        self.tls_chk.grid(row=5, column=0, sticky="w", padx=12, pady=6)

        self.remember_chk = ctk.CTkCheckBox(self, text="Remember secret (keyring)")
        self.remember_chk.grid(row=5, column=1, sticky="e", padx=12, pady=6)

        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.grid(row=6, column=0, columnspan=2, sticky="ew", padx=12, pady=(8, 4))
        btn_row.grid_columnconfigure((0, 1), weight=1)

        self.test_btn = ctk.CTkButton(btn_row, text="Test MinIO", command=self.test_connection)
        self.test_btn.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.clear_btn = ctk.CTkButton(btn_row, text="Clear", fg_color="gray", hover_color="#6b7280", command=self.clear_fields)
        self.clear_btn.grid(row=0, column=1, sticky="ew", padx=(6, 0))

        self.status = ctk.CTkLabel(self, text="", wraplength=420, justify="left")
        self.status.grid(row=7, column=0, columnspan=2, sticky="ew", padx=12, pady=(6, 12))

    # --- IO helpers ---
    def get_prefs(self) -> dict:
        return {
            "minio_endpoint": self.endpoint_entry.get().strip(),
            "minio_access_key": self.access_key_entry.get().strip(),
            "minio_bucket": self.bucket_entry.get().strip(),
            "minio_tls": int(self.tls_chk.get() == 1),
            "remember_minio": int(self.remember_chk.get() == 1),
        }

    def set_prefs(self, data: dict, password_loader=None):
        self.endpoint_entry.delete(0, "end"); self.endpoint_entry.insert(0, data.get("minio_endpoint", ""))
        self.access_key_entry.delete(0, "end"); self.access_key_entry.insert(0, data.get("minio_access_key", ""))
        self.bucket_entry.delete(0, "end"); self.bucket_entry.insert(0, data.get("minio_bucket", ""))
        if data.get("minio_tls"): self.tls_chk.select()
        else: self.tls_chk.deselect()
        if data.get("remember_minio"): self.remember_chk.select()
        else: self.remember_chk.deselect()
        if callable(password_loader) and data.get("remember_minio"):
            key = f"minio:{(data.get('minio_access_key') or 'default')}@{(data.get('minio_endpoint') or 'localhost')}"
            pwd = password_loader(user=key)
            if pwd:
                self.secret_entry.delete(0, "end")
                self.secret_entry.insert(0, pwd)

    def get_secret(self) -> str:
        return self.secret_entry.get()

    def is_connection_valid(self) -> bool:
        """Check if the MinIO connection has been tested successfully."""
        # If config changed since last test, connection is no longer valid
        current_config = self._get_config_fingerprint()
        if current_config != self._last_tested_config:
            self._connection_valid = False
        return self._connection_valid

    def _get_config_fingerprint(self) -> str:
        """Get a fingerprint of current config to detect changes."""
        return f"{self.endpoint_entry.get()}|{self.access_key_entry.get()}|{self.bucket_entry.get()}|{self.tls_chk.get()}"

    # --- Actions ---
    def _build_urls(self) -> list[str]:
        endpoint = (self.endpoint_entry.get() or "").strip()
        if not endpoint:
            return []
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            base = endpoint
        else:
            scheme = "https" if bool(self.tls_chk.get()) else "http"
            base = f"{scheme}://{endpoint}"
        return [
            f"{base}/minio/health/ready",
            f"{base}/minio/health/live",
        ]

    def test_connection(self):
        self.status.configure(text="Connecting to MinIO…")
        self.update_idletasks()
        self._connection_valid = False  # Reset until proven valid
        urls = self._build_urls()
        if not urls:
            self.status.configure(text="⚠️ Missing MinIO endpoint.")
            if callable(self.on_change):
                self.on_change()
            return
        ok = False
        error_msg = None
        for url in urls:
            try:
                req = urllib.request.Request(url, method="GET")
                with urllib.request.urlopen(req, timeout=4) as resp:
                    if 200 <= resp.status < 300:
                        ok = True
                        break
                    else:
                        error_msg = f"HTTP {resp.status}"
            except urllib.error.HTTPError as e:
                error_msg = f"HTTPError {e.code}: {e.reason}"
            except urllib.error.URLError as e:
                error_msg = f"URLError: {e.reason}"
            except Exception as e:
                error_msg = f"{e.__class__.__name__}: {e}"
        if ok:
            base = urls[0].rsplit('/minio', 1)[0]
            bucket = (self.bucket_entry.get() or "").strip().strip("/")
            if bucket:
                ak = (self.access_key_entry.get() or "").strip()
                sk = (self.secret_entry.get() or "").strip()
                if ak and sk:
                    # Auth check: head bucket then try zero-byte put and delete to assert write
                    try:
                        import uuid  # type: ignore
                        import boto3  # type: ignore
                        from botocore.exceptions import ClientError  # type: ignore
                        from botocore.config import Config  # type: ignore

                        s3 = boto3.client(
                            "s3",
                            endpoint_url=base,
                            aws_access_key_id=ak,
                            aws_secret_access_key=sk,
                            region_name="us-east-1",
                            config=Config(signature_version="s3v4", s3={"addressing_style": "path"}),
                        )
                        # Does bucket exist and are we authorized to access it?
                        try:
                            s3.head_bucket(Bucket=bucket)
                        except ClientError as ce:
                            resp = getattr(ce, "response", {}) or {}
                            http_status = (resp.get("ResponseMetadata", {}) or {}).get("HTTPStatusCode", None)
                            error_code = (resp.get("Error", {}) or {}).get("Code", "")
                            if error_code in ("404", "NoSuchBucket") or http_status == 404:
                                self.status.configure(text=f"❌ Bucket '{bucket}' not found at {base}")
                                if callable(self.on_change):
                                    self.on_change()
                                return
                            else:
                                self.status.configure(text=f"❌ Cannot access bucket '{bucket}' with given credentials ({error_code or http_status})")
                                if callable(self.on_change):
                                    self.on_change()
                                return

                        # Try to PUT zero-byte object to verify write permission
                        probe_key = f".probe_{uuid.uuid4().hex}"
                        try:
                            s3.put_object(Bucket=bucket, Key=probe_key, Body=b"")
                            # Best-effort delete to not leave artifacts
                            try:
                                s3.delete_object(Bucket=bucket, Key=probe_key)
                            except Exception:
                                pass
                            self._connection_valid = True
                            self._last_tested_config = self._get_config_fingerprint()
                            self.status.configure(text=f"✅ Can send to bucket '{bucket}' at {base}")
                            if callable(self.on_save):
                                self.on_save()
                        except ClientError as ce:
                            resp = getattr(ce, "response", {}) or {}
                            http_status = (resp.get("ResponseMetadata", {}) or {}).get("HTTPStatusCode", None)
                            error_code = (resp.get("Error", {}) or {}).get("Code", "")
                            self.status.configure(text=f"❌ Cannot write to bucket '{bucket}' with given credentials ({error_code or http_status})")
                        except Exception as e:
                            self.status.configure(text=f"❌ Cannot write to bucket '{bucket}' ({e.__class__.__name__}: {e})")
                    except Exception as e:
                        # boto3 not present or init failed; cannot verify auth write
                        # Mark as valid with warning - user takes responsibility
                        self._connection_valid = True
                        self._last_tested_config = self._get_config_fingerprint()
                        self.status.configure(text=f"⚠️ MinIO is reachable at {base} • Install boto3 to verify bucket access")
                else:
                    # No credentials provided - NOT valid for sending
                    self.status.configure(text=f"⚠️ MinIO is reachable at {base} • Provide access/secret to verify bucket access")
            else:
                # No bucket specified - NOT valid for sending
                self.status.configure(text=f"⚠️ MinIO is reachable at {base} • Specify a bucket to send data")
            if callable(self.on_save):
                self.on_save()
        else:
            self.status.configure(text=f"❌ MinIO check failed: {error_msg or 'Unknown error'}")
        if callable(self.on_change):
            self.on_change()

    def clear_fields(self):
        for w in (self.endpoint_entry, self.access_key_entry, self.bucket_entry, self.secret_entry):
            w.delete(0, "end")
        self.tls_chk.deselect()
        self.remember_chk.deselect()
        self.status.configure(text="")
        self._connection_valid = False
        self._last_tested_config = None
        if callable(self.on_change):
            self.on_change()

