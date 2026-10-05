import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "healthy"}

def test_load_sample_project():
    res = client.post("/api/projects/sample")
    assert res.status_code == 200
    data = res.json()
    assert data["name"] == "sample-buggy-project"
    assert data["language"] == "TypeScript"
    assert data["framework"] == "Express"

def test_get_project_not_found():
    res = client.get("/api/projects/non-existent-id")
    assert res.status_code == 404
