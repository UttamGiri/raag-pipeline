import pytest

@pytest.mark.integration
def test_rag_returns_sources_and_metadata(base_url, session):
    """Verify RAG query returns sources with complete metadata"""
    q = "Explain the refund process."

    resp = session.post(f"{base_url}/query",
                        json={"query": q, "top_k": 5, "include_metadata": True})
    assert resp.status_code == 200

    data = resp.json()
    assert "sources" in data

    src = data["sources"][0]
    assert "score" in src
    assert "s3_bucket" in src or "s3_key" in src
    assert "has_pii" in src

@pytest.mark.integration
def test_unrecognized_query_gracefully_handles_no_results(base_url, session):
    """Test graceful handling when no relevant documents are found"""
    payload = {"query": "asldkfjasldkfjasldkfjasldkf", "top_k": 5}
    resp = session.post(f"{base_url}/query", json=payload)

    assert resp.status_code == 200
    data = resp.json()

    assert "answer" in data
    assert "sources" in data
    assert len(data["sources"]) == 0 or data["sources"][0]["score"] < 0.2

