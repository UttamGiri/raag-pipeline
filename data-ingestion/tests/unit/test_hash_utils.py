from src.hashing.hash_utils import sha256_hash

def test_hash():
    h = sha256_hash("abc")
    assert len(h) == 64 #A correct SHA-256 hex digest must ALWAYS be 64 characters


