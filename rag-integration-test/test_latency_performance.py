import time
import pytest

@pytest.mark.integration
def test_p95_latency_under_2_seconds(base_url, session):
    """Test that 95th percentile latency is under 2 seconds"""
    latencies = []

    for _ in range(20):
        start = time.time()
        resp = session.post(f"{base_url}/query", json={"query": "Explain tax refund process"})
        assert resp.status_code == 200
        latencies.append(time.time() - start)

    latencies.sort()
    p95 = latencies[int(0.95 * len(latencies))]

    assert p95 < 2.0, f"P95 latency too high: {p95}"

