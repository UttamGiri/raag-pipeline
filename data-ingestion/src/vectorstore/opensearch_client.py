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
                    # Content fields
                    "content_redacted":{"type":"text"},
                    "content_hash":{"type":"keyword"},
                    "has_pii":{"type":"boolean"},
                    "vector":{"type":"knn_vector","dimension":dim,
                              "method":{"name":"hnsw","space_type":"cosinesimil","engine":"nmslib"}},
                    
                    # Document metadata (mandatory)
                    "document_id":{"type":"keyword"},
                    "s3_bucket":{"type":"keyword"},
                    "s3_key":{"type":"keyword"},
                    "doc_type":{"type":"keyword"},
                    
                    # Organizational metadata (mandatory)
                    "department":{"type":"keyword"},
                    "division":{"type":"keyword"},
                    "team":{"type":"keyword"},
                    "roles_allowed":{"type":"keyword"},  # Array of roles
                    
                    # Search & retrieval metadata
                    "chunk_id":{"type":"keyword"},
                    "chunk_index":{"type":"integer"},
                    "page_number":{"type":"integer"},
                    
                    # Compliance & audit metadata
                    "ingestion_date":{"type":"date"},
                    "ingested_by":{"type":"keyword"},
                    "pii_detected":{"type":"keyword"},  # Array of PII types
                    "embedding_model":{"type":"keyword"},
                    "embedding_model_version":{"type":"keyword"},
                    "chunker_version":{"type":"keyword"},
                    
                    # Optional metadata
                    "title":{"type":"text"},
                    "version":{"type":"keyword"},
                    "tags":{"type":"keyword"},  # Array of tags
                    "classification":{"type":"keyword"},
                    "security_level":{"type":"keyword"},
                    "owner":{"type":"keyword"},
                    "data_domain":{"type":"keyword"},
                    "source_url":{"type":"keyword"},
                    "effective_date":{"type":"date"},
                    "last_review_date":{"type":"date"},
                }
            }
        }
        self.client.indices.create(self.index, body)

    def index_docs(self, chunks, vectors, hashes, pii_flags, pii_detected_list, meta, chunk_metadata_list=None):
        """
        Index documents with rich metadata.
        
        Args:
            chunks: List of redacted text chunks
            vectors: List of embedding vectors
            hashes: List of content hashes
            pii_flags: List of boolean flags indicating PII presence
            pii_detected_list: List of lists containing detected PII types per chunk
            meta: Base metadata dictionary (document-level)
            chunk_metadata_list: Optional list of chunk-specific metadata (chunk_index, page_number, etc.)
        """
        if chunk_metadata_list is None:
            chunk_metadata_list = [{}] * len(chunks)
        
        for idx, (text, vec, h, flag, pii_detected, chunk_meta) in enumerate(
            zip(chunks, vectors, hashes, pii_flags, pii_detected_list, chunk_metadata_list)
        ):
            # Generate chunk_id if not provided
            chunk_id = chunk_meta.get("chunk_id", f"{meta.get('document_id', 'doc')}-chunk-{idx}")
            
            doc = {
                "content_redacted": text,
                "content_hash": h,
                "has_pii": flag,
                "vector": vec,
                "chunk_id": chunk_id,
                "chunk_index": chunk_meta.get("chunk_index", idx),
                "page_number": chunk_meta.get("page_number"),
                "pii_detected": pii_detected if pii_detected else [],
                **meta
            }
            # Remove None values
            doc = {k: v for k, v in doc.items() if v is not None}
            self.client.index(self.index, body=doc)

