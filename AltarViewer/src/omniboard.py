"""Omniboard Docker container management."""
import subprocess
import socket
import hashlib
import uuid
import sys
import time
import os
import shutil
from typing import List, Optional
from urllib.parse import urlparse, urlunparse


class OmniboardManager:
    """Manages Omniboard Docker containers."""
    
    @staticmethod
    def _docker_cmd_base() -> List[str]:
        """Resolve the Docker CLI executable path.

        Returns a list representing the base command to invoke Docker, ensuring
        it works in frozen executables where PATH may be limited.
        """
        # Prefer system PATH resolution
        path = shutil.which("docker")
        if path:
            return [path]
        # Windows default installation paths
        candidates = [
            r"C:\\Program Files\\Docker\\Docker\\resources\\bin\\docker.exe",
            r"C:\\Program Files\\Docker\\Docker\\resources\\bin\\com.docker.cli.exe",
        ]
        # Common Unix/Mac locations
        candidates.extend([
            "/usr/bin/docker",
            "/usr/local/bin/docker",
            "/opt/homebrew/bin/docker",
        ])
        for c in candidates:
            if os.path.exists(c):
                return [c]
        # Fallback to plain 'docker' (may still succeed if shell resolves it)
        return ["docker"]
    
    @staticmethod
    def is_docker_running() -> bool:
        """Check if Docker daemon is running.
        
        Returns:
            True if Docker is running, False otherwise
        """
        try:
            base = OmniboardManager._docker_cmd_base()
            # First try a lightweight version check
            result = subprocess.run(
                base + ["version", "--format", "{{.Server.Version}}"],
                capture_output=True,
                text=True,
                timeout=8,
            )
            if result.returncode == 0 and result.stdout.strip():
                return True
            # Fallback to info with formatting
            result2 = subprocess.run(
                base + ["info", "--format", "{{.ServerVersion}}"],
                capture_output=True,
                text=True,
                timeout=8,
            )
            return result2.returncode == 0 and result2.stdout.strip() != ""
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    @staticmethod
    def start_docker_desktop():
        """Attempt to start Docker Desktop.
        
        Raises:
            Exception: If Docker Desktop cannot be started
        """
        if sys.platform.startswith("win"):
            # Windows
            subprocess.Popen(
                ["powershell", "-Command", "Start-Process", "'C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe'"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        elif sys.platform == "darwin":
            # macOS
            subprocess.Popen(
                ["open", "-a", "Docker"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        else:
            # Linux - typically systemd
            subprocess.Popen(
                ["systemctl", "start", "docker"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        # Wait up to 60 seconds for Docker to start
        for _ in range(60):
            time.sleep(1)
            if OmniboardManager.is_docker_running():
                return
        
        raise Exception("Docker Desktop failed to start within 60 seconds")
    
    @staticmethod
    def ensure_docker_running():
        """Ensure Docker is running, start it if needed.
        
        Raises:
            Exception: If Docker cannot be started
        """
        if not OmniboardManager.is_docker_running():
            OmniboardManager.start_docker_desktop()
    
    @staticmethod
    def generate_port_for_database(db_name: str, base: int = 20000, span: int = 10000) -> int:
        """Generate a deterministic port number based on database name.
        
        Args:
            db_name: Database name
            base: Base port number
            span: Port range span
            
        Returns:
            Port number
        """
        h = int(hashlib.sha256(db_name.encode()).hexdigest(), 16)
        return base + (h % span)
    
    @staticmethod
    def find_available_port(start_port: int) -> int:
        """Find an available port starting from the given port.
        
        Args:
            start_port: Starting port to search from
            
        Returns:
            Available port number
        """
        port = start_port
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(("", port))
                    # Also check if Docker is using this port
                    try:
                        result = subprocess.run(
                            OmniboardManager._docker_cmd_base()
                            + ["ps", "--filter", f"publish={port}", "--format", "{{.ID}}"],
                            capture_output=True,
                            text=True,
                            timeout=5
                        )
                        if result.stdout.strip() == "":
                            return port
                    except (subprocess.TimeoutExpired, FileNotFoundError):
                        return port
                except OSError:
                    port += 1
    
    
    def launch(
        self,
        db_name: str,
        mongo_host: str,
        mongo_port: int,
        host_port: Optional[int] = None,
        mongo_uri: Optional[str] = None,
    ) -> tuple[str, int]:
        """Launch an Omniboard Docker container.
        
        Args:
            db_name: Database name to connect to
            mongo_host: MongoDB host
            mongo_port: MongoDB port
            host_port: Optional host port (will find available if not provided)
            mongo_uri: Optional full MongoDB connection URI. When provided,
                Omniboard will be launched with this URI (using --mu) and the
                selected database will be injected into the URI path.
            
        Returns:
            Tuple of (container_name, host_port)
            
        Raises:
            Exception: If Docker launch fails
        """
        # Ensure Docker is running
        self.ensure_docker_running()
        
        # Find an available port if not specified
        if host_port is None:
            preferred_port = self.generate_port_for_database(db_name)
            host_port = self.find_available_port(preferred_port)
        
        container_name = f"omniboard_{uuid.uuid4().hex[:8]}"

        # Decide whether to use full URI or host:port:db form
        if mongo_uri:
            # Build a Docker-adjusted URI and ensure DB is included in the path
            mongo_arg = self._adjust_mongo_uri_for_docker(mongo_uri, db_name=db_name)
            mongo_flag = "--mu"
        else:
            # Port mode: when connecting to a MongoDB running on the host,
            # containers cannot reach the host via 127.0.0.1.
            # Use host.docker.internal on Windows/macOS and the default Docker
            # bridge gateway (172.17.0.1) on Linux.
            host_for_container = mongo_host
            if mongo_host in ("localhost", "127.0.0.1"):
                if sys.platform.startswith("linux"):
                    host_for_container = "172.17.0.1"
                else:
                    host_for_container = "host.docker.internal"
            mongo_arg = f"{host_for_container}:{mongo_port}:{db_name}"
            mongo_flag = "-m"

        # Build Docker command (detached)
        docker_cmd = OmniboardManager._docker_cmd_base() + [
            "run", "-d", "--rm",
            "-p", f"127.0.0.1:{host_port}:9000",
            "--name", container_name,
            "vivekratnavel/omniboard",
            mongo_flag, mongo_arg,
        ]
        
        # Launch container
        subprocess.Popen(
            docker_cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
        )
        
        return container_name, host_port
    
    @staticmethod
    def list_containers() -> List[str]:
        """List all Omniboard container IDs.
        
        Returns:
            List of container IDs
        """
        try:
            result = subprocess.run(
                OmniboardManager._docker_cmd_base()
                + [
                    "ps",
                    "-a",
                    "--filter",
                    "name=omniboard_",
                    "--format",
                    "{{.ID}}",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.stdout.strip().splitlines()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return []
    
    def clear_all_containers(self) -> int:
        """Remove all Omniboard Docker containers.
        
        Returns:
            Number of containers removed
        """
        container_ids = self.list_containers()
        
        if not container_ids:
            return 0
        
        for cid in container_ids:
            try:
                subprocess.run(
                    OmniboardManager._docker_cmd_base() + ["rm", "-f", cid],
                    timeout=10,
                )
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass
        
        return len(container_ids)

    def _adjust_mongo_uri_for_docker(self, mongo_uri: str, db_name: Optional[str] = None) -> str:
        """Inject DB name into a full MongoDB URI and preserve credentials and query.

        Host resolution adjustments are intentionally not performed.
        """
        try:
            parsed = urlparse(mongo_uri)
        except Exception:
            # If parsing fails, return original URI
            return mongo_uri

        # Reconstruct netloc with potential creds and port (no host rewriting)
        userinfo = ""
        if parsed.username:
            userinfo += parsed.username
            if parsed.password:
                userinfo += f":{parsed.password}"
            userinfo += "@"
        port_part = f":{parsed.port}" if parsed.port else ""
        netloc = f"{userinfo}{parsed.hostname or ''}{port_part}"

        # Always set the path to the selected DB if provided
        path = parsed.path or ""
        if db_name:
            path = f"/{db_name}"

        adjusted = urlunparse((
            parsed.scheme,
            netloc,
            path,
            "",
            parsed.query,
            "",
        ))
        return adjusted