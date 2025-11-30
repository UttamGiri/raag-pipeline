import re
import pytest

PII_PATTERNS = [
    r"\b\d{3}-\d{2}-\d{4}\b",                # SSN
    r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",     # Email
    r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", # Phone
    r"\b\d{16}\b"                            # Credit card
]

@pytest.mark.integration
def test_no_pii_in_indexed_chunks(base_url, session):
    """Verify no PII patterns are present in indexed chunks"""
    resp = session.get(f"{base_url}/debug/index/chunks")
    chunks = resp.json()

    for chunk in chunks:
        text = chunk["text"]
        for p in PII_PATTERNS:
            assert re.search(p, text) is None

@pytest.mark.integration
def test_hash_stored_instead_of_raw_pii(base_url, session):
    """Verify raw PII is replaced with hashes"""
    resp = session.get(f"{base_url}/debug/index/chunks")
    chunks = resp.json()

    for ch in chunks:
        assert "hash" in ch
        assert len(ch["hash"]) == 64  # SHA-256 hex

