from src.chunking.semantic_chunker import semantic_split

def test_semantic_split_basic():
    chunks = semantic_split("Hello world. This is a test.")
    assert len(chunks) >= 1

