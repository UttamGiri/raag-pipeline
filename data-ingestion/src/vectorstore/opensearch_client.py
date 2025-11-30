import os
from opensearchpy import OpenSearch, RequestsHttpConnection
from src.utils.logger import get_logger

logger = get_logger(__name__)

class OpenSearchVectorStore:

    def __init__(self):
        endpoint = os.getenv("OPENSEARCH_ENDPOINT")
        self.index = os.getenv("OPENSEARCH_INDEX")

        self.client = OpenSearch(
            hosts=[{"host": endpoint.replace("https://",""), "port":443}],
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )

    def create_if_not_exists(self, dim):
        if self.client.indices.exists(self.index):
            return
        body = {
            "settings":{"index":{"knn":True}},
            "mappings":{
                "properties":{
                    "content_redacted":{"type":"text"},
                    "content_hash":{"type":"keyword"},
                    "has_pii":{"type":"boolean"},
                    "vector":{"type":"knn_vector","dimension":dim,
                              "method":{"name":"hnsw","space_type":"cosinesimil","engine":"nmslib"}},
                    "s3_bucket":{"type":"keyword"},
                    "s3_key":{"type":"keyword"},
                }
            }
        }
        self.client.indices.create(self.index, body)

    def index_docs(self, chunks, vectors, hashes, pii_flags, meta):
        for text, vec, h, flag in zip(chunks, vectors, hashes, pii_flags):
            doc = {
                "content_redacted": text,
                "content_hash": h,
                "has_pii": flag,
                "vector": vec,
                **meta
            }
            self.client.index(self.index, body=doc)

