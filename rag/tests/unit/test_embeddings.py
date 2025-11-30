from unittest.mock import patch, MagicMock

from src.embeddings.cohere_bedrock_embeddings import CohereBedrockEmbedder

@patch("src.embeddings.cohere_bedrock_embeddings.settings")
@patch("src.embeddings.cohere_bedrock_embeddings.boto3.client")
def test_embed_query_returns_vector(mock_boto_client, mock_settings):
    mock_settings.aws_region = "us-east-1"
    mock_settings.bedrock_cohere_model = "cohere.embed-english-v3"
    
    mock_runtime = MagicMock()
    mock_runtime.invoke_model.return_value = {
        "body": MagicMock(read=lambda: b'{"embeddings":[[0.1,0.2,0.3]]}')
    }
    mock_boto_client.return_value = mock_runtime

    embedder = CohereBedrockEmbedder()
    vec = embedder.embed_query("hello world")

    assert vec == [0.1, 0.2, 0.3]
    mock_runtime.invoke_model.assert_called_once()

