import pytest
from main import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    res = client.get("/")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"

def test_shorten_url(client):
    res = client.post("/api/shorten", json={"url": "https://example.com"})
    data = res.get_json()
    assert res.status_code == 201
    assert "short_code" in data
    assert data["short_url"].endswith(data["short_code"])

def test_redirect(client):
    res = client.post("/api/shorten", json={"url": "https://google.com"})
    short_code = res.get_json()["short_code"]
    redir = client.get(f"/{short_code}", follow_redirects=False)
    assert redir.status_code == 302
    assert "google.com" in redir.location

def test_stats(client):
    res = client.post("/api/shorten", json={"url": "https://test.com"})
    short_code = res.get_json()["short_code"]
    client.get(f"/{short_code}")
    stats = client.get(f"/api/stats/{short_code}")
    data = stats.get_json()
    assert stats.status_code == 200
    assert data["clicks"] == 1
    assert data["url"] == "https://test.com"
    assert "created_at" in data

def test_invalid_url(client):
    res = client.post("/api/shorten", json={"url": "not_a_url"})
    assert res.status_code == 400
