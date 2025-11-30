import boto3
import json
from typing import List

from src.config.settings import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

class CohereBedrockEmbedder:
    """
    Wrapper for Cohere embed-english-v3 via Amazon Bedrock.
    Used for query embeddings in the RAG service.
    """

    def __init__(self):
        self.region = settings.aws_region
        self.model_id = settings.bedrock_cohere_model
        if not self.model_id:
            raise ValueError("BEDROCK_COHERE_MODEL is not set")
        self.client = boto3.client("bedrock-runtime", region_name=self.region)

    def embed_query(self, text: str) -> List[float]:
        if not text.strip():
            raise ValueError("Query must not be empty for embedding")
        logger.debug(f"Embedding query with model {self.model_id}")

        body = json.dumps({"texts": [text]})
        resp = self.client.invoke_model(
            modelId=self.model_id,
            contentType="application/json",
            accept="application/json",
            body=body,
        )
        payload = json.loads(resp["body"].read())
        # Cohere format: {"embeddings": [[...]]}
        return payload["embeddings"][0]

