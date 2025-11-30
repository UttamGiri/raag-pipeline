import os
from datetime import datetime
from dotenv import load_dotenv
from src.loaders.s3_pdf_loader import read_pdf_from_s3
from src.chunking.semantic_chunker import semantic_split
from src.pii.pii_presidio import PiiPresidioService
from src.hashing.hash_utils import sha256_hash
from src.embeddings.cohere_bedrock_embeddings import CohereBedrockEmbedder
from src.vectorstore.opensearch_client import OpenSearchVectorStore
from src.utils.logger import get_logger

logger = get_logger(__name__)

def _parse_list_env(env_var: str, default=None):
    """Parse comma-separated environment variable into list."""
    value = os.getenv(env_var, "")
    if not value:
        return default or []
    return [item.strip() for item in value.split(",") if item.strip()]

def _build_metadata():
    """Build comprehensive metadata from environment variables."""
    # Mandatory fields
    document_id = os.getenv("DOCUMENT_ID")
    if not document_id:
        # Generate from S3 key if not provided
        key = os.getenv("S3_PDF_KEY", "")
        document_id = key.replace("/", "-").replace(".pdf", "") or "unknown-doc"
    
    department = os.getenv("DEPARTMENT", "")
    if not department:
        raise ValueError("DEPARTMENT environment variable is required")
    
    roles_allowed = _parse_list_env("ROLES_ALLOWED", [])
    if not roles_allowed:
        raise ValueError("ROLES_ALLOWED environment variable is required (comma-separated)")
    
    # Build metadata dictionary
    meta = {
        # Document metadata (mandatory)
        "document_id": document_id,
        "s3_bucket": os.getenv("S3_BUCKET_NAME"),
        "s3_key": os.getenv("S3_PDF_KEY"),
        "doc_type": os.getenv("DOC_TYPE", "PDF"),
        
        # Organizational metadata (mandatory)
        "department": department,
        "division": os.getenv("DIVISION", ""),
        "team": os.getenv("TEAM", ""),
        "roles_allowed": roles_allowed,
        
        # Compliance & audit metadata
        "ingestion_date": datetime.utcnow().isoformat() + "Z",
        "ingested_by": os.getenv("INGESTED_BY", os.getenv("USER", "unknown")),
        "embedding_model": os.getenv("BEDROCK_COHERE_MODEL", "cohere.embed-english-v2"),
        "embedding_model_version": os.getenv("EMBEDDING_MODEL_VERSION", "2.0"),
        "chunker_version": os.getenv("CHUNKER_VERSION", "semantic-1.0"),
        
        # Optional metadata
        "title": os.getenv("DOCUMENT_TITLE", ""),
        "version": os.getenv("DOCUMENT_VERSION", ""),
        "tags": _parse_list_env("TAGS", []),
        "classification": os.getenv("CLASSIFICATION", ""),
        "security_level": os.getenv("SECURITY_LEVEL", ""),
        "owner": os.getenv("OWNER", ""),
        "data_domain": os.getenv("DATA_DOMAIN", ""),
        "source_url": os.getenv("SOURCE_URL", ""),
    }
    
    # Remove empty optional fields
    meta = {k: v for k, v in meta.items() if v or k in [
        "document_id", "s3_bucket", "s3_key", "department", "roles_allowed",
        "ingestion_date", "ingested_by", "embedding_model"
    ]}
    
    return meta

def run_pipeline():
    # Load environment variables
    env = os.getenv("ENVIRONMENT", "dev")
    env_file = f"env/.env.{env}"
    if os.path.exists(env_file):
        load_dotenv(env_file)
    else:
        load_dotenv()  # Fallback to default .env if exists
    
    bucket = os.getenv("S3_BUCKET_NAME")
    key = os.getenv("S3_PDF_KEY")
    
    if not bucket or not key:
        raise ValueError("S3_BUCKET_NAME and S3_PDF_KEY must be set")

    logger.info(f"Starting ingestion for s3://{bucket}/{key}")
    text = read_pdf_from_s3(bucket, key)

    # semantic chunking
    chunks = semantic_split(text)
    logger.info(f"Split document into {len(chunks)} chunks")

    # PII Redaction
    pii = PiiPresidioService()
    redacted = []
    pii_flags = []
    pii_detected_list = []
    hashes = []

    for ch in chunks:
        r, flag, detected = pii.redact(ch)
        redacted.append(r)
        pii_flags.append(flag)
        pii_detected_list.append(detected)
        hashes.append(sha256_hash(ch))

    # embeddings
    embedder = CohereBedrockEmbedder()
    vectors = embedder.embed(redacted)
    dim = len(vectors[0])
    logger.info(f"Generated embeddings with dimension {dim}")

    # Build metadata
    meta = _build_metadata()
    
    # Create chunk metadata (chunk_index for each chunk)
    chunk_metadata_list = [
        {"chunk_index": idx}
        for idx in range(len(chunks))
    ]

    # index
    os_client = OpenSearchVectorStore()
    os_client.create_if_not_exists(dim)
    
    os_client.index_docs(
        chunks=redacted,
        vectors=vectors,
        hashes=hashes,
        pii_flags=pii_flags,
        pii_detected_list=pii_detected_list,
        meta=meta,
        chunk_metadata_list=chunk_metadata_list
    )

    logger.info(f"Ingestion complete. Indexed {len(chunks)} chunks for document {meta.get('document_id')}")

if __name__ == "__main__":
    run_pipeline()

