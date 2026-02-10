"""Tests for Docker detection and GUI behavior regarding manual start requirement."""
import os
import sys
import subprocess
import types
import pytest

from src.omniboard import OmniboardManager


def test_docker_cmd_base_uses_candidates(monkeypatch):
    """When docker is not on PATH, fallback candidates should be considered."""
    # Simulate no docker on PATH
    monkeypatch.setattr("shutil.which", lambda name: None)

    # Pretend one Windows candidate exists regardless of platform
    def fake_exists(path: str) -> bool:
        return path.endswith("com.docker.cli.exe")

    monkeypatch.setattr("os.path.exists", fake_exists)

    base = OmniboardManager._docker_cmd_base()
    assert isinstance(base, list) and base
    assert base[0].endswith("com.docker.cli.exe")


def test_is_docker_running_prefers_version(monkeypatch):
    """is_docker_running should return True when `docker version` succeeds."""

    def fake_run(args, capture_output=False, text=False, timeout=None):
        class R:
            def __init__(self, rc, out=""):
                self.returncode = rc
                self.stdout = out
                self.stderr = ""
        if "version" in args:
            return R(0, "25.0.3\n")
        return R(1, "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    assert OmniboardManager.is_docker_running() is True


def test_is_docker_running_fallback_info(monkeypatch):
    """If version fails but info works, detection should still succeed."""

    def fake_run(args, capture_output=False, text=False, timeout=None):
        class R:
            def __init__(self, rc, out=""):
                self.returncode = rc
                self.stdout = out
                self.stderr = ""
        if "version" in args:
            return R(1, "")
        if "info" in args:
            return R(0, "25.0.3\n")
        return R(1, "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    assert OmniboardManager.is_docker_running() is True


@pytest.mark.skipif(os.environ.get("DISPLAY") is None and not sys.platform.startswith("win"),
                    reason="Tk requires a display; skip on headless CI")
def test_gui_does_not_autostart(monkeypatch):
    """GUI should not auto-start Docker; it should prompt the user and return."""
    from src.gui import MongoApp

    # Instantiate the app (headless);
    app = MongoApp()

    # Select a database so launch_omniboard proceeds to docker checks
    app.selected_db.set("mydb")

    # Mock docker running check to return False
    monkeypatch.setattr(app.omniboard_manager, "is_docker_running", lambda: False)

    # Ensure start_docker_desktop is not called
    start_called = {"v": False}

    def fake_start():
        start_called["v"] = True

    monkeypatch.setattr(app.omniboard_manager, "start_docker_desktop", fake_start)

    # Stub messagebox to capture info messages without showing dialogs
    infos = []

    monkeypatch.setattr("src.gui.messagebox.showinfo", lambda *a, **k: infos.append(a[0]))
    monkeypatch.setattr("src.gui.messagebox.showerror", lambda *a, **k: None)

    # Attempt to launch
    app.launch_omniboard()

    # Assert no auto-start and that a message was shown
    assert start_called["v"] is False
    assert infos and "Docker not running" in infos[0]

    # Cleanup the Tk app
    app.destroy()
