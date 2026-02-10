"""Unit tests for Omniboard manager module."""
import pytest
import sys
from src.omniboard import OmniboardManager


class TestOmniboardManager:
    """Test Omniboard manager functionality."""
    
    def test_generate_port_for_database(self):
        """Test deterministic port generation."""
        manager = OmniboardManager()
        
        # Same database should always get same port
        port1 = manager.generate_port_for_database("test_db")
        port2 = manager.generate_port_for_database("test_db")
        assert port1 == port2
        
        # Different databases should get different ports
        port3 = manager.generate_port_for_database("other_db")
        assert port1 != port3
        
        # Port should be in valid range
        assert 20000 <= port1 < 30000
    
    def test_generate_port_custom_range(self):
        """Test port generation with custom range."""
        manager = OmniboardManager()
        port = manager.generate_port_for_database("test", base=5000, span=1000)
        assert 5000 <= port < 6000
    
    def test_adjust_mongo_uri_injects_db_and_preserves_host(self):
        """Ensure DB is injected into URI without rewriting host."""
        manager = OmniboardManager()
        # Localhost example
        uri = "mongodb://user:pass@localhost:27017/?replicaSet=rs0"
        adjusted = manager._adjust_mongo_uri_for_docker(uri, db_name="mydb")
        assert adjusted.startswith("mongodb://user:pass@localhost:27017/")
        assert "/mydb" in adjusted
        assert "replicaSet=rs0" in adjusted
        # Remote host example
        uri2 = "mongodb://user:pass@mongo.example.com:27017/"
        adjusted2 = manager._adjust_mongo_uri_for_docker(uri2, db_name="abc")
        assert "mongo.example.com:27017/abc" in adjusted2
    
    def test_find_available_port(self):
        """Test finding available port."""
        manager = OmniboardManager()
        
        # Should find a port (this is a basic smoke test)
        port = manager.find_available_port(25000)
        assert port >= 25000
        assert isinstance(port, int)
    
    def test_list_containers(self):
        """Test listing containers."""
        manager = OmniboardManager()
        
        # Should return a list (empty or with IDs)
        containers = manager.list_containers()
        assert isinstance(containers, list)
