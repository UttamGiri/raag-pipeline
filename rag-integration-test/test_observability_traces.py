import pytest

@pytest.mark.integration
def test_trace_header_propagation(base_url, session):
    """Validate trace header propagation for observability"""
    resp = session.post(f"{base_url}/query", json={"query": "What is refund?"})
    assert resp.status_code == 200

    trace_id = resp.headers.get("x-trace-id")
    assert trace_id is not None
    assert len(trace_id) > 10

    # Check trace exists in Jaeger (optional)
    # jaeger_query = requests.get(f"http://jaeger/api/traces/{trace_id}")
    # assert jaeger_query.status_code == 200

