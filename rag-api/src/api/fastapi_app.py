from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

from src.config.settings import settings
from src.utils.logger import get_logger
from src.embeddings.cohere_bedrock_embeddings import CohereBedrockEmbedder
from src.retrieval.opensearch_retriever import OpenSearchRetriever
from src.llm.claude_bedrock_client import ClaudeBedrockClient

logger = get_logger(__name__)
app = FastAPI(title="RAG Query Service")

# Instantiate dependencies once (can be swapped with DI in bigger project)
embedder = CohereBedrockEmbedder()
retriever = OpenSearchRetriever()
llm_client = ClaudeBedrockClient()

class QueryRequest(BaseModel):
    query: str
    top_k: int = 5

class Source(BaseModel):
    score: float
    content: str
    has_pii: bool | None = None
    s3_bucket: str | None = None
    s3_key: str | None = None

class QueryResponse(BaseModel):
    answer: str
    sources: List[Source]

@app.get("/health")
def health_check():
    return {"status": "ok", "environment": settings.environment}

@app.post("/query", response_model=QueryResponse)
def query_endpoint(payload: QueryRequest):
    query = payload.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query must not be empty")

    logger.info(f"Received query: {query}")

    # 1. Embed query
    q_vec = embedder.embed_query(query)

    # 2. Retrieve documents
    docs = retriever.retrieve(q_vec, k=payload.top_k)
    if not docs:
        logger.info("No documents retrieved from OpenSearch.")
        return QueryResponse(
            answer="I couldn't find any relevant information in the knowledge base.",
            sources=[],
        )

    contexts = [d["content"] for d in docs]

    # 3. Call Claude LLM with contexts
    answer = llm_client.answer(query, contexts)

    sources_response = [
        Source(
            score=d["score"],
            content=d["content"],
            has_pii=d.get("has_pii"),
            s3_bucket=d.get("s3_bucket"),
            s3_key=d.get("s3_key"),
        )
        for d in docs
    ]

    return QueryResponse(answer=answer, sources=sources_response)

