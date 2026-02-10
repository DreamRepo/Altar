import json
import os
from pathlib import Path
from typing import Optional

try:
    from platformdirs import user_config_dir  # type: ignore
except Exception:
    user_config_dir = None  # Fallback to legacy path if platformdirs missing

try:
    import keyring  # type: ignore
except ImportError:  # keyring is optional; methods will no-op if unavailable
    keyring = None

KEYRING_SERVICE = "AltarViewer"

# Determine stable, OS-appropriate config path
if user_config_dir:
    _config_dir = Path(user_config_dir("AltarViewer", "DreamRepo"))
else:
    # Fallback: avoid relying on HOME if it points to a non-user location
    # Prefer APPDATA on Windows, else default to Path.home()
    base = Path(os.getenv("APPDATA", str(Path.home())))
    _config_dir = base / "AltarViewer"

_config_dir.mkdir(parents=True, exist_ok=True)
CONFIG_PATH = _config_dir / "config.json"

# Legacy location used by older versions; read-only fallback
LEGACY_CONFIG_PATH = Path.home() / ".altarviewer_config.json"

class Preferences:
    def is_keyring_available(self) -> bool:
        return keyring is not None

    def load(self) -> dict:
        try:
            if CONFIG_PATH.exists():
                return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            # Backward compatibility: read legacy config if present
            if LEGACY_CONFIG_PATH.exists():
                return json.loads(LEGACY_CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
        return {}

    def save_without_password(self, data: dict):
        # Ensure password is never written to disk
        clean = dict(data)
        for k in ("password", "pwd"):
            if k in clean:
                clean.pop(k)
        try:
            CONFIG_PATH.write_text(json.dumps(clean, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    def save_password_if_allowed(self, remember: bool, user: str, password: str):
        if not keyring:
            return
        try:
            if remember and password:
                keyring.set_password(KEYRING_SERVICE, user, password)
            else:
                try:
                    keyring.delete_password(KEYRING_SERVICE, user)
                except Exception:
                    pass
        except Exception:
            pass

    def load_password_if_any(self, user: str) -> Optional[str]:
        if not keyring:
            return None
        try:
            return keyring.get_password(KEYRING_SERVICE, user)
        except Exception:
            return None
