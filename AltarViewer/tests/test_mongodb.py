"""Unit tests for MongoDB client module."""
import pytest
from src.mongodb import MongoDBClient


class TestMongoDBClient:
    """Test MongoDB client functionality."""
    
    def test_init(self):
        """Test client initialization."""
        client = MongoDBClient()
        assert client.client is None
        assert client.uri is None
    
    def test_parse_connection_url_default(self):
        """Test URL parsing with no connection."""
        client = MongoDBClient()
        host, port, db = client.parse_connection_url()
        assert host == "localhost"
        assert port == 27017
        assert db is None
    
    def test_parse_connection_url_with_port(self):
        """Test URL parsing after port connection."""
        client = MongoDBClient()
        client.uri = "mongodb://localhost:27018/"
        host, port, db = client.parse_connection_url()
        assert host == "localhost"
        assert port == 27018
        assert db is None
    
    def test_parse_connection_url_with_database(self):
        """Test URL parsing with database in path."""
        client = MongoDBClient()
        client.uri = "mongodb://localhost:27017/mydb"
        host, port, db = client.parse_connection_url()
        assert host == "localhost"
        assert port == 27017
        assert db == "mydb"
    
    def test_parse_connection_url_custom_host(self):
        """Test URL parsing with custom host."""
        client = MongoDBClient()
        client.uri = "mongodb://192.168.1.100:27017/"
        host, port, db = client.parse_connection_url()
        assert host == "192.168.1.100"
        assert port == 27017
        assert db is None
    
    def test_connect_by_url_validation(self):
        """Test URL connection validation."""
        client = MongoDBClient()
        with pytest.raises(ValueError, match="URL cannot be empty"):
            client.connect_by_url("")
    
    def test_connect_by_url_adds_protocol(self):
        """Test that protocol is added if missing."""
        client = MongoDBClient()
        # This will fail connection but we can check URI was set correctly
        try:
            client.connect_by_url("localhost:27017")
        except:
            pass
        assert client.uri.startswith("mongodb://")
