import boto3, os, json
from typing import List
try:
    from langchain_core.embeddings import Embeddings
except ImportError:
    # Fallback for older langchain versions
    try:
        from langchain.embeddings.base import Embeddings
    except ImportError:
        # Create a simple ABC if langchain is not available
        from abc import ABC, abstractmethod
        class Embeddings(ABC):
            @abstractmethod
            def embed_documents(self, texts: List[str]) -> List[List[float]]:
                pass
            @abstractmethod
            def embed_query(self, text: str) -> List[float]:
                pass

from src.utils.logger import get_logger

logger = get_logger(__name__)

class CohereBedrockEmbedder(Embeddings):

    def __init__(self):
        self.region = os.getenv("AWS_REGION","us-east-1")
        self.model = os.getenv("BEDROCK_COHERE_MODEL")
        self.client = boto3.client("bedrock-runtime", region_name=self.region)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents using Cohere Bedrock."""
        vectors = []
        for t in texts:
            body = json.dumps({"texts":[t]})
            resp = self.client.invoke_model(
                modelId=self.model,
                contentType="application/json",
                accept="application/json",
                body=body
            )
            payload = json.loads(resp["body"].read())
            vectors.append(payload["embeddings"][0])
        return vectors

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query using Cohere Bedrock."""
        body = json.dumps({"texts":[text]})
        resp = self.client.invoke_model(
            modelId=self.model,
            contentType="application/json",
            accept="application/json",
            body=body
        )
        payload = json.loads(resp["body"].read())
        return payload["embeddings"][0]

    def embed(self, texts):
        """Legacy method for backward compatibility."""
        return self.embed_documents(texts if isinstance(texts, list) else [texts])

