import os
from dotenv import load_dotenv
from src.loaders.s3_pdf_loader import read_pdf_from_s3
from src.chunking.semantic_chunker import semantic_split
from src.pii.pii_presidio import PiiPresidioService
from src.hashing.hash_utils import sha256_hash
from src.embeddings.cohere_bedrock_embeddings import CohereBedrockEmbedder
from src.vectorstore.opensearch_client import OpenSearchVectorStore
from src.utils.logger import get_logger

logger = get_logger(__name__)

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

    text = read_pdf_from_s3(bucket, key)

    # semantic chunking
    chunks = semantic_split(text)

    # PII Redaction
    pii = PiiPresidioService()
    redacted = []
    pii_flags = []
    hashes = []

    for ch in chunks:
        r, flag = pii.redact(ch)
        redacted.append(r)
        pii_flags.append(flag)
        hashes.append(sha256_hash(ch))

    # embeddings
    embedder = CohereBedrockEmbedder()
    vectors = embedder.embed(redacted)
    dim = len(vectors[0])

    # index
    os_client = OpenSearchVectorStore()
    os_client.create_if_not_exists(dim)

    meta = {"s3_bucket": bucket, "s3_key": key}
    os_client.index_docs(redacted, vectors, hashes, pii_flags, meta)

    logger.info("Ingestion complete.")

if __name__ == "__main__":
    run_pipeline()

