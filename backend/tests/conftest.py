import pytest
import os
import sys

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Set up test environment variables"""
    os.environ["POSTGRES_HOST"] = "localhost"
    os.environ["POSTGRES_USER"] = "postgres"
    os.environ["POSTGRES_PASSWORD"] = "postgres"
    os.environ["POSTGRES_DB"] = "realestate_test"
    os.environ["JWT_SECRET"] = "test-secret-key"
    os.environ["REDIS_URL"] = "redis://localhost:6379/1"  # Use different Redis DB for tests
