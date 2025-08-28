from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_requires_org_header_on_business_routes():
    assert client.get("/clients").status_code == 401
    assert client.get("/technicians").status_code == 401
    assert client.get("/interventions").status_code == 401
    assert client.get("/interventions/1/events").status_code == 401

def test_endpoints_exist_but_not_implemented_with_org():
    headers = {"X-Org-ID": "org_alpha"}
    assert client.get("/clients", headers=headers).status_code == 501
    assert client.get("/technicians", headers=headers).status_code == 501
    assert client.get("/interventions", headers=headers).status_code == 501
    assert client.get("/interventions/1/events", headers=headers).status_code == 501

def test_login_endpoint_exists():
    r = client.post("/auth/login", data={"username": "fake", "password": "fake"})
    assert r.status_code in [401, 422]

AUTH_HEADERS = {"Authorization": "Bearer faketoken123"}
def test_list_interventions_returns_200():
    r = client.get("/interventions", headers=AUTH_HEADERS)
    assert r.status_code == 200
    assert isinstance(r.json().get("interventions"), list) or r.status_code == 501
