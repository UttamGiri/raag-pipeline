from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient

from src.api.fastapi_app import app

client = TestClient(app)

@patch("src.api.fastapi_app.llm_client")
@patch("src.api.fastapi_app.retriever")
@patch("src.api.fastapi_app.embedder")
def test_query_endpoint_success(mock_embedder, mock_retriever, mock_llm):
    mock_embedder.embed_query.return_value = [0.1, 0.2]

    mock_retriever.retrieve.return_value = [
        {
            "score": 1.0,
            "content": "Context doc",
            "has_pii": False,
            "s3_bucket": "bucket",
            "s3_key": "key",
        }
    ]

    mock_llm.answer.return_value = "Final answer"

    response = client.post(
        "/query",
        json={"query": "What is this?", "top_k": 3},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "Final answer"
    assert len(data["sources"]) == 1

