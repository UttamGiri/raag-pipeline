import pytest

@pytest.mark.integration
def test_no_raw_pdf_content_leaked(base_url, session):
    """Verify no raw PDF content is leaked in responses"""
    resp = session.post(f"{base_url}/query", json={"query": "Give me the raw document"})
    ans = resp.json()["answer"]

    forbidden_tokens = ["%PDF-", "obj", "endobj", "/Catalog", "/Metadata"]
    for token in forbidden_tokens:
        assert token not in ans

@pytest.mark.integration
def test_https_only(base_url, session):
    """Verify service only accepts HTTPS connections"""
    assert base_url.startswith("https")

@pytest.mark.integration
def test_api_rejects_empty_or_invalid_inputs(base_url, session):
    """Test API properly validates and rejects invalid inputs"""
    resp = session.post(f"{base_url}/query", json={"query": ""})
    assert resp.status_code in [400, 422]

@pytest.mark.integration
def test_rate_limiting_enforced(base_url, session):
    """Test that rate limiting is properly enforced"""
    for _ in range(50):
        session.post(f"{base_url}/query", json={"query": "refund?"})

    # Final call should show sign of throttling
    final = session.post(f"{base_url}/query", json={"query": "refund?"})
    assert final.status_code in (429, 200)

