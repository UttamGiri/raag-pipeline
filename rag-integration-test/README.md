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

## Running Integration Tests (3 Supported Methods)

Your project includes a full external integration test suite located in:

```
rag-integration-test/
```

These tests validate the deployed RAG service, not your local code. They must run against a real environment such as staging.

Below are the 3 supported methods to run integration tests.

### 🟦 Option 1 — Run Integration Tests Locally (Fastest & Easiest)

⭐ **Recommended for developers**  
⭐ **Best when CI takes too long**  
⭐ **Most commonly used approach**

#### Prerequisites

- RAG API must already be deployed to staging.
- You must know the staging endpoint, e.g.:
  ```
  https://rag-staging.myagency.gov
  ```

#### Run locally:

```bash
cd rag-integration-test
export RAG_BASE_URL="https://rag-staging.myagency.gov"
pytest -m integration -vv
```

#### Why this is the best method

- ✅ Fastest feedback loop
- ✅ No need to deploy code
- ✅ No need to run the CI/CD pipeline
- ✅ Ideal for SDET, QA, and devs
- ✅ Tests hit the REAL deployed environment

### Option 2 — Run via CI/CD Pipeline

(To be documented)

### Option 3 — Run in Container/Remote Environment

(To be documented)

## Quick Start (Local Development)

For local development and testing:

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

