import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

from app.main import app
from app.deps import get_db, init_db
from app.models import Base

# Test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    # Create test database
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    # Clean up
    Base.metadata.drop_all(bind=engine)

def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome" in response.json()["message"]

def test_register_user(client):
    response = client.post(
        "/api/v1/register",
        json={
            "username": "testuser",
            "password": "testpass123",
            "email": "test@example.com"
        }
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

def test_login_user(client):
    # First register a user
    client.post(
        "/api/v1/register",
        json={
            "username": "logintest",
            "password": "testpass123",
            "email": "login@example.com"
        }
    )
    
    # Then try to login
    response = client.post(
        "/api/v1/token",
        data={
            "username": "logintest",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_get_listings_unauthorized(client):
    response = client.get("/api/v1/listings")
    assert response.status_code == 401

def test_get_listings_authorized(client):
    # Register and login
    client.post(
        "/api/v1/register",
        json={
            "username": "listingstest",
            "password": "testpass123",
            "email": "listings@example.com"
        }
    )
    
    login_response = client.post(
        "/api/v1/token",
        data={
            "username": "listingstest",
            "password": "testpass123"
        }
    )
    token = login_response.json()["access_token"]
    
    # Get listings with auth
    response = client.get(
        "/api/v1/listings",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "listings" in response.json()
