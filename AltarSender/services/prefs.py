import json
from pathlib import Path

try:
    import keyring
except ImportError:
    keyring = None

CONFIG_PATH = Path.home() / ".mongoui_config.json"
KEYRING_SERVICE = "MongoDBLoginCustomTk"

class Preferences:
    def load(self) -> dict:
        try:
            return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def save_without_password(self, data: dict):
        # never write the password in the JSON config
        data = dict(data)
        if "password" in data:
            data.pop("password")
        try:
            CONFIG_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    def save_password_if_allowed(self, remember: bool, user: str, password: str):
        if not keyring:
            return
        try:
            if remember and password:
                keyring.set_password(KEYRING_SERVICE, user, password)
            else:
                # supprimer s'il existe
                try:
                    keyring.delete_password(KEYRING_SERVICE, user)
                except Exception:
                    pass
        except Exception:
            pass

    def load_password_if_any(self, user: str) -> str | None:
        if not keyring:
            return None
        try:
            return keyring.get_password(KEYRING_SERVICE, user)
        except Exception:
            return None
