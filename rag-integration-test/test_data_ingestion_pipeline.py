import pytest
import requests
import time

@pytest.mark.integration
def test_ingestion_pipeline_runs_successfully(ingestion_url, session):
    """Verify full ingestion flow: PDF → S3 → extract → chunk → redact → embed → index → retrieve"""
    payload = {
        "bucket": "my-test-bucket",
        "key": "sample.pdf"
    }
    resp = session.post(f"{ingestion_url}/ingestion/run", json=payload)
    assert resp.status_code == 200
    assert resp.json().get("status") == "success"

@pytest.mark.integration
def test_ingestion_creates_expected_number_of_chunks(ingestion_url, session):
    """Verify ingestion produces a reasonable number of chunks"""
    resp = session.get(f"{ingestion_url}/ingestion/last-run")
    assert resp.status_code == 200

    data = resp.json()
    assert "num_chunks" in data
    assert data["num_chunks"] > 5  # adjust threshold

@pytest.mark.integration
def test_ingestion_index_contains_metadata(ingestion_url, session):
    """Verify indexed documents contain required metadata"""
    resp = session.get(f"{ingestion_url}/debug/index/metadata")
    assert resp.status_code == 200

    meta = resp.json()
    assert "s3_bucket" in meta
    assert "s3_key" in meta
    assert "timestamp" in meta

