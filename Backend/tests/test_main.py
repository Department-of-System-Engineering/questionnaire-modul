from fastapi.testclient import TestClient
from src.main import app
import unittest

class TestHealthCheck(unittest.TestCase):
    def test_health_check(self):
        """Test the health check endpoint"""
        client = TestClient(app)
        response = client.get("/api/dev_tools/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}