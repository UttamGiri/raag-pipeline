import os

import requests

def test_smoke_query_against_running_service():
    """
    Simple smoke test. Assumes service is running locally on port 8000.
    Mark or skip this in CI if not needed.
    """
    base_url = os.getenv("RAG_URL", "http://localhost:8000")
    resp = requests.get(f"{base_url}/health")
    assert resp.status_code == 200

