import pytest

@pytest.mark.integration
def test_smoke_query_against_running_service(base_url, session):
    """
    Simple smoke test. Assumes service is running locally on port 8000.
    Mark or skip this in CI if not needed.
    """
    resp = session.get(f"{base_url}/health")
    assert resp.status_code == 200

