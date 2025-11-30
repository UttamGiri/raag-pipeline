from unittest.mock import patch, MagicMock

from src.retrieval.opensearch_retriever import OpenSearchRetriever

@patch("src.retrieval.opensearch_retriever.settings")
@patch("src.retrieval.opensearch_retriever.OpenSearch")
def test_retrieve_returns_shaped_docs(mock_os, mock_settings):
    mock_settings.opensearch_endpoint = "https://example.com"
    mock_settings.opensearch_index = "rag_documents_dev"

    mock_client = MagicMock()
    mock_client.search.return_value = {
        "hits": {
            "hits": [
                {
                    "_score": 1.23,
                    "_source": {
                        "content_redacted": "Doc1 content",
                        "has_pii": False,
                        "s3_bucket": "bucket",
                        "s3_key": "key1",
                    },
                }
            ]
        }
    }
    mock_os.return_value = mock_client

    retriever = OpenSearchRetriever()
    docs = retriever.retrieve([0.1, 0.2], k=1)

    assert len(docs) == 1
    assert docs[0]["content"] == "Doc1 content"
    assert docs[0]["score"] == 1.23
    mock_client.search.assert_called_once()

