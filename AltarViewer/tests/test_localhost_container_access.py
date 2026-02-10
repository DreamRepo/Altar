"""Tests for Port mode localhost mapping to host.docker.internal on Desktop platforms."""
import sys
import subprocess

from src.omniboard import OmniboardManager


def _capture_popen(monkeypatch):
    recorded = {"args": None}

    class DummyPopen:
        def __init__(self, args, **kwargs):
            recorded["args"] = args
        # Provide minimal interface
        def communicate(self, *a, **k):
            return ("", "")

    monkeypatch.setattr(subprocess, "Popen", DummyPopen)
    return recorded


def test_port_mode_maps_localhost_on_windows(monkeypatch):
    recorded = _capture_popen(monkeypatch)
    # Pretend Docker is running and docker command base is just ['docker']
    monkeypatch.setattr(OmniboardManager, "ensure_docker_running", lambda self: None)
    monkeypatch.setattr(sys, "platform", "win32", raising=False)

    m = OmniboardManager()
    # Choose a fixed port to avoid find_available_port
    container, host_port = m.launch(
        db_name="mydb",
        mongo_host="localhost",
        mongo_port=27017,
        host_port=25001,
        mongo_uri=None,
    )

    args = recorded["args"]
    assert args is not None
    # Ensure '-m' is present and the argument uses host.docker.internal
    assert "-m" in args
    idx = args.index("-m")
    assert args[idx + 1].startswith("host.docker.internal:27017:")


def test_port_mode_keeps_remote_hosts(monkeypatch):
    recorded = _capture_popen(monkeypatch)
    monkeypatch.setattr(OmniboardManager, "ensure_docker_running", lambda self: None)
    monkeypatch.setattr(sys, "platform", "darwin", raising=False)

    m = OmniboardManager()
    m.launch(
        db_name="db2",
        mongo_host="mongo.example.com",
        mongo_port=27018,
        host_port=25002,
        mongo_uri=None,
    )

    args = recorded["args"]
    assert args is not None
    idx = args.index("-m")
    assert args[idx + 1] == "mongo.example.com:27018:db2"


def test_port_mode_maps_localhost_on_linux(monkeypatch):
    recorded = _capture_popen(monkeypatch)
    monkeypatch.setattr(OmniboardManager, "ensure_docker_running", lambda self: None)
    monkeypatch.setattr(sys, "platform", "linux", raising=False)

    m = OmniboardManager()
    m.launch(
        db_name="ldb",
        mongo_host="localhost",
        mongo_port=27017,
        host_port=25003,
        mongo_uri=None,
    )

    args = recorded["args"]
    assert args is not None
    idx = args.index("-m")
    # On Linux we expect the Docker bridge gateway IP
    assert args[idx + 1].startswith("172.17.0.1:27017:")
