import pytest

@pytest.mark.integration
def test_chunk_lengths_within_bounds(base_url, session):
    """Validate semantic chunking produces chunks within size bounds"""
    resp = session.get(f"{base_url}/debug/chunks")
    chunks = resp.json()

    for ch in chunks:
        assert 200 <= len(ch["text"]) <= 2500

@pytest.mark.integration
def test_chunks_have_overlap(base_url, session):
    """Verify chunks have semantic overlap to preserve context"""
    resp = session.get(f"{base_url}/debug/chunks")
    chunks = resp.json()

    overlaps = 0
    for i in range(len(chunks)-1):
        if chunks[i]["text"][-100:] in chunks[i+1]["text"]:
            overlaps += 1

    assert overlaps >= 1

@pytest.mark.integration
def test_chunking_preserves_headings(base_url, session):
    """Ensure chunking preserves document structure like headings"""
    resp = session.get(f"{base_url}/debug/chunks")
    chunks = resp.json()

    headings = [c for c in chunks if c["text"].strip().startswith("#")]
    assert len(headings) > 0

