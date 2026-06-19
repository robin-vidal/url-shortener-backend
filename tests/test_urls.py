import os
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_shorten_returns_code_and_short_url():
    response = client.post("/shorten", json={"url": "https://example.com"})
    assert response.status_code == 200
    data = response.json()
    assert "code" in data
    assert "short_url" in data


def test_shorten_code_length():
    response = client.post("/shorten", json={"url": "https://example.com"})
    code = response.json()["code"]
    assert len(code) == 6


def test_shorten_two_urls_get_different_codes():
    r1 = client.post("/shorten", json={"url": "https://example.com"})
    r2 = client.post("/shorten", json={"url": "https://other.com"})
    assert r1.json()["code"] != r2.json()["code"]


def test_shorten_missing_url_returns_422():
    response = client.post("/shorten", json={})
    assert response.status_code == 422


def test_redirect():
    code = client.post("/shorten", json={"url": "https://example.com"}).json()["code"]
    response = client.get(f"/r/{code}", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["location"] == "https://example.com"


def test_redirect_increments_clicks():
    from app.models import URL
    code = client.post("/shorten", json={"url": "https://example.com"}).json()["code"]
    client.get(f"/r/{code}", follow_redirects=False)
    client.get(f"/r/{code}", follow_redirects=False)
    db = TestingSessionLocal()
    entry = db.query(URL).filter(URL.code == code).first()
    db.close()
    assert entry.clicks == 2


def test_redirect_not_found():
    response = client.get("/nonexistent", follow_redirects=False)
    assert response.status_code == 404


def test_list_urls_empty():
    response = client.get("/urls")
    assert response.status_code == 200
    assert response.json() == []


def test_list_urls_returns_all():
    client.post("/shorten", json={"url": "https://example.com"})
    client.post("/shorten", json={"url": "https://other.com"})
    response = client.get("/urls")
    assert len(response.json()) == 2


def test_list_urls_most_recent_first():
    client.post("/shorten", json={"url": "https://first.com"})
    client.post("/shorten", json={"url": "https://second.com"})
    urls = client.get("/urls").json()
    assert urls[0]["original"] == "https://second.com"
