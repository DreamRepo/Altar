"""MongoDB client management."""
from pymongo import MongoClient
from pymongo.errors import OperationFailure
from typing import List, Optional
from urllib.parse import urlparse, parse_qs
import importlib.util


class MongoDBClient:
    """Handles MongoDB connections and database operations."""
    
    def __init__(self):
        """Initialize MongoDB client."""
        self.client: Optional[MongoClient] = None
        self.uri: Optional[str] = None
    
    def connect_by_port(self, port: str = "27017") -> List[str]:
        """Connect to MongoDB using localhost and port.
        
        Args:
            port: MongoDB port number
            
        Returns:
            List of database names
            
        Raises:
            Exception: If connection fails
        """
        self.uri = f"mongodb://localhost:{port}/"
        return self._connect()
    
    def connect_by_url(self, url: str) -> List[str]:
        """Connect to MongoDB using full URL.
        
        Args:
            url: MongoDB connection URL
            
        Returns:
            List of database names
            
        Raises:
            Exception: If connection fails
        """
        if not url:
            raise ValueError("URL cannot be empty")
        
        # Ensure proper protocol
        if not url.startswith("mongodb://") and not url.startswith("mongodb+srv://"):
            url = "mongodb://" + url

        # If using SRV, ensure dnspython is available (required by PyMongo)
        parsed = urlparse(url)
        if parsed.scheme == "mongodb+srv":
            if importlib.util.find_spec("dns") is None:
                raise RuntimeError(
                    "The 'mongodb+srv://' scheme requires the 'dnspython' package. "
                    "Please install it (e.g., pip install dnspython) or use a standard 'mongodb://' URI."
                )
        
        self.uri = url
        return self._connect()
    
    def _connect(self) -> List[str]:
        """Internal method to establish connection and list databases.
        
        Returns:
            List of database names
            
        Raises:
            Exception: If connection fails
        """
        if self.client:
            self.client.close()
        
        self.client = MongoClient(self.uri, serverSelectionTimeoutMS=3000)
        try:
            # Standard behaviour: attempt to list all databases. This
            # requires appropriate permissions (typically admin-level).
            return self.client.list_database_names()
        except OperationFailure as exc:
            # Some deployments (Atlas/VM with non-admin user) forbid
            # listDatabases. Fall back to the database inside the URI
            # so the GUI can proceed with selection and Omniboard launch.
            msg = str(exc).lower()
            if "listdatabases" in msg or "not authorized" in msg or "command listdatabases" in msg:
                _, _, database = self.parse_connection_url()
                if database:
                    return [database]
                # If no DB path was provided, try to infer from authSource
                try:
                    parsed = urlparse(self.uri or "")
                    params = parse_qs(parsed.query)
                    auth_source = params.get("authSource", [None])[0]
                    if auth_source:
                        return [auth_source]
                except Exception:
                    pass
            # Otherwise, re-raise the original error
            raise
    
    def parse_connection_url(self) -> tuple[str, int, Optional[str]]:
        """Parse the current connection URL.
        
        Returns:
            Tuple of (host, port, database)
        """
        if not self.uri:
            return "localhost", 27017, None
        
        parsed = urlparse(self.uri)
        host = parsed.hostname or "localhost"
        port = parsed.port or 27017
        database = parsed.path.strip("/") if parsed.path else None
        database = database if database else None  # Convert empty string to None
        
        return host, port, database
    
    def get_connection_uri(self) -> Optional[str]:
        """Return the current MongoDB connection URI (if any)."""
        return self.uri
    
    def close(self):
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            self.client = None