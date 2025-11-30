import os
import pytest
import requests

@pytest.fixture(scope="session")
def base_url():
    """Base URL for the RAG service."""
    return os.getenv("RAG_URL", "http://localhost:8000")

@pytest.fixture(scope="session")
def ingestion_url():
    """Base URL for the data ingestion service."""
    return os.getenv("INGESTION_URL", "http://localhost:8001")

@pytest.fixture(scope="session")
def session():
    """HTTP session for making requests."""
    return requests.Session()

