# Data Ingestion Microservice (RAG Pipeline)

This microservice:

1. Downloads a PDF from Amazon S3  
2. Extracts text using PyPDF  
3. Performs semantic chunking using LangChain  
4. Redacts PII/PHI using Microsoft Presidio  
5. Hashes raw text using SHA-256 (one-way)  
6. Generates embeddings using Cohere `embed-english-v2` via Bedrock  
7. Indexes redacted chunks + vectors into OpenSearch  

## Architecture

This microservice implements a complete RAG (Retrieval-Augmented Generation) data ingestion pipeline with a modular, production-ready architecture. Each component is designed to be independently testable and replaceable.

### Key Components

**Semantic Chunking**: Uses Cohere Bedrock embeddings (`embed-english-v2`) with LangChain's `SemanticChunker` to intelligently split documents into semantically meaningful chunks. The chunking process considers:
- Maximum chunk size (default: 1000 characters, configurable via `MAX_CHUNK_SIZE`)
- Minimum chunk size (default: 200 characters, configurable via `MIN_CHUNK_SIZE`)
- Breakpoint threshold type (`percentile`, `standard_deviation`, or `interquartile`)

**PII/PHI Redaction**: Leverages [Microsoft Presidio](https://microsoft.github.io/presidio/) with spaCy's `en_core_web_lg` model to detect and redact sensitive information. Presidio uses a combination of pattern matching, context analysis, and NLP-based detection methods to identify PII/PHI entities.

**Currently Detected Entities** (configurable in `src/pii/pii_presidio.py`):
- **Global Entities**: `PERSON`, `PHONE_NUMBER`, `EMAIL_ADDRESS`, `IP_ADDRESS`, `CREDIT_CARD`, `DATE_TIME`, `LOCATION`, `MEDICAL_LICENSE`
- **US-Specific**: `US_SSN` (Social Security Number)
- **Medical**: `HEALTH_INSURANCE_POLICY_NUMBER`


For a complete list of supported entities, see the [Presidio Supported Entities documentation](https://microsoft.github.io/presidio/supported_entities/).

**Detection Methods**: Presidio employs multiple detection strategies:
- Pattern matching with regex and validation (checksums, format validation)
- Context analysis using NLP models
- Custom logic for complex entities
- Integration with external services (Azure AI Language, Azure Health Data Services)

The service can be extended to detect additional entity types by modifying the `entities` list in the `PiiPresidioService` class.

**Embedding Generation**: Utilizes Cohere's `embed-english-v2` model through AWS Bedrock for high-quality vector representations. The embedder implements LangChain's `Embeddings` interface, making it compatible with the semantic chunker and other LangChain components.

**Vector Storage**: Indexes documents in OpenSearch with:
- KNN vector search capabilities (HNSW algorithm with cosine similarity)
- Metadata tracking (S3 source, PII flags, content hashes)
- Support for semantic search queries

## Configuration

### Environment Variables

The service supports multiple environments (dev, staging, prod) through separate `.env` files:

- `ENVIRONMENT`: Current environment (dev/staging/prod)
- `AWS_REGION`: AWS region for S3 and Bedrock
- `S3_BUCKET_NAME`: S3 bucket containing PDFs
- `S3_PDF_KEY`: S3 key/path to the PDF file
- `OPENSEARCH_ENDPOINT`: OpenSearch cluster endpoint
- `OPENSEARCH_INDEX`: Target index name
- `BEDROCK_COHERE_MODEL`: Cohere model ID (default: `cohere.embed-english-v2`)
- `MAX_CHUNK_SIZE`: Maximum chunk size in characters (default: 1000)
- `MIN_CHUNK_SIZE`: Minimum chunk size in characters (default: 200)
- `BREAKPOINT_THRESHOLD_TYPE`: Chunking threshold type (default: `percentile`)

### Running the Pipeline

```bash
# Set environment
export ENVIRONMENT=dev

# Run pipeline
python -m src.pipelines.ingestion_pipeline
```

### Docker Deployment

```bash
# Build image
docker build -t data-ingestion:latest .

# Run container
docker run --env-file env/.env.dev data-ingestion:latest
```

## Testing

Run the test suite:

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html
```

## Features

Supports:
- dev / staging / prod `.env` environments  
- Docker-based deployment  
- Modular architecture  
- Full unit test suite (pytest)
- Configurable semantic chunking with Cohere Bedrock embeddings
- Comprehensive PII/PHI detection and redaction
- Content deduplication via SHA-256 hashing
- Production-ready logging and error handling

