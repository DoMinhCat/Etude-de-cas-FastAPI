from fastapi.testclient import TestClient

from app.core.security import create_access_token
from app.main import app

client = TestClient(app)

sample_client = {"sub": "client_user", "org_id": 1, "role": "client"}
sample_tech = {"sub": "tech_user", "org_id": 1, "role": "tech"}
client_token = create_access_token(sample_client)
tech_token = create_access_token(sample_tech)

client_headers = {"Authorization": f"Bearer {client_token}"}
tech_headers = {"Authorization": f"Bearer {tech_token}"}

def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_list_endpoints_require_auth():
    assert client.get("/clients").status_code == 401
    assert client.get("/technicians").status_code == 401
    assert client.get("/items").status_code == 401
    assert client.get("/interventions/12/events").status_code == 401

def test_list_endpoints_with_auth():
    r = client.get("/clients", headers=client_headers)
    assert r.status_code in [200, 404, 501]  

    r = client.get("/technicians", headers=tech_headers)
    assert r.status_code in [200, 404, 501]

    r = client.get("/interventions", headers=client_headers)
    assert r.status_code in [200, 404, 501]

    r = client.get("/interventions", headers=tech_headers)
    assert r.status_code in [200, 404, 501]

    r = client.get("/interventions/1/events", headers=tech_headers)
    assert r.status_code in [200, 404, 501]

def test_login_endpoint_exists():
    r = client.post("/auth/login", data={"username": "fake", "password": "fake"})
    assert r.status_code in [401, 422]
