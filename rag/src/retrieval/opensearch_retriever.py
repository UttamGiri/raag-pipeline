from typing import List, Dict, Any

from opensearchpy import OpenSearch, RequestsHttpConnection

from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

class OpenSearchRetriever:

    def __init__(self):
        endpoint = settings.opensearch_endpoint
        index = settings.opensearch_index
        if not endpoint:
            raise ValueError("OPENSEARCH_ENDPOINT is not set")

        self.index = index
        self.client = OpenSearch(
            hosts=[{"host": endpoint.replace("https://", ""), "port": 443}],
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
        )
        logger.info(f"OpenSearchRetriever using index={self.index}")

    def retrieve(self, query_vector: list[float], k: int = 5) -> List[Dict[str, Any]]:
        body = {
            "size": k,
            "query": {
                "knn": {
                    "vector": {
                        "vector": query_vector,
                        "k": k,
                    }
                }
            },
            "_source": [
                "content_redacted",
                "has_pii",
                "s3_bucket",
                "s3_key",
            ],
        }

        resp = self.client.search(index=self.index, body=body)
        hits = resp["hits"]["hits"]
        logger.debug(f"Retriever returned {len(hits)} hits")

        docs = []
        for h in hits:
            src = h["_source"]
            docs.append(
                {
                    "score": h["_score"],
                    "content": src.get("content_redacted", ""),
                    "has_pii": src.get("has_pii", False),
                    "s3_bucket": src.get("s3_bucket"),
                    "s3_key": src.get("s3_key"),
                }
            )
        return docs

