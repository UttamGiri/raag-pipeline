import pytest

GOLDEN = [
    {
        "q": "Which form reports wage income?",
        "keywords": ["w-2"],
        "min_score": 0.80
    },
    {
        "q": "When is the tax filing deadline?",
        "keywords": ["april", "15"],
        "min_score": 0.75
    },
]

@pytest.mark.integration
@pytest.mark.parametrize("case", GOLDEN)
def test_retrieval_accuracy_for_known_questions(base_url, session, case):
    """Test retrieval accuracy against golden question-answer pairs"""
    resp = session.post(f"{base_url}/query", json={"query": case["q"], "top_k": 5})
    assert resp.status_code == 200

    data = resp.json()
    sources = data["sources"]

    assert len(sources) > 0
    assert sources[0]["score"] >= case["min_score"]

    answer = data["answer"].lower()
    for kw in case["keywords"]:
        assert kw in answer

