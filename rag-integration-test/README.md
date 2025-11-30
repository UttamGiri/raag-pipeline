# RAG Integration Tests

This directory contains end-to-end integration tests for the RAG pipeline, testing both the data ingestion and RAG query services together.

## Test Coverage

- **Data Ingestion Pipeline**: Full flow from PDF to indexed documents
- **Chunking Quality**: Semantic chunking validation
- **PII Redaction**: Security and privacy validation
- **Retrieval Accuracy**: Vector search quality
- **RAG Query Functional**: End-to-end query functionality
- **LLM Safety**: Jailbreak defense and bias testing
- **Performance**: Latency and throughput metrics
- **Observability**: Trace propagation and monitoring
- **Security Controls**: Input validation, rate limiting, content leakage

## Running Tests

```bash
# Install dependencies
pip install -r ../rag/requirements.txt

# Set service URLs (optional, defaults to localhost)
export RAG_URL=http://localhost:8000
export INGESTION_URL=http://localhost:8001

# Run all integration tests
pytest

# Run specific test file
pytest test_retrieval_accuracy.py

# Skip integration tests
pytest -m "not integration"
```

## Prerequisites

- Both RAG and data ingestion services must be running
- OpenSearch cluster must be accessible
- AWS credentials configured for Bedrock access

