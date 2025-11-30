from unittest.mock import patch, MagicMock
from src.embeddings.cohere_bedrock_embeddings import CohereBedrockEmbedder

@patch("src.embeddings.cohere_bedrock_embeddings.boto3.client")
def test_embedding(mock_client):
    mock_runtime = MagicMock()
    mock_client.return_value = mock_runtime
    mock_runtime.invoke_model.return_value = {
        "body": MagicMock(read=lambda: b'{"embeddings":[[0.1,0.2]]}')
    }

    emb = CohereBedrockEmbedder()
    out = emb.embed(["hello"])
    assert out == [[0.1,0.2]]

