"""Integration tests for the application."""
import pytest


class TestIntegration:
    """Test integration between modules."""
    
    def test_imports(self):
        """Test that all modules can be imported."""
        from src.mongodb import MongoDBClient
        from src.omniboard import OmniboardManager
        
        # Basic instantiation
        mongo = MongoDBClient()
        omni = OmniboardManager()
        
        assert mongo is not None
        assert omni is not None
    
    def test_workflow_simulation(self):
        """Test a typical workflow without actual connections."""
        from src.mongodb import MongoDBClient
        from src.omniboard import OmniboardManager
        
        # Initialize clients
        mongo = MongoDBClient()
        omni = OmniboardManager()
        
        # Simulate URL setup
        mongo.uri = "mongodb://localhost:27017/"
        host, port, _ = mongo.parse_connection_url()
        
        assert host == "localhost"
        assert port == 27017
        
        # Simulate port generation for a database
        db_name = "test_database"
        preferred_port = omni.generate_port_for_database(db_name)
        
        assert isinstance(preferred_port, int)
        assert 20000 <= preferred_port < 30000
        
        # No host adjustment is performed anymore; use host as-is
        assert host == "localhost"
