import os
from dotenv import load_dotenv
try:
    from pydantic_settings import BaseSettings
except ImportError:
    # Fallback for pydantic < 2.0
    from pydantic import BaseSettings

class Settings(BaseSettings):
    environment: str = "dev"
    aws_region: str = "us-east-1"

    opensearch_endpoint: str
    opensearch_index: str

    bedrock_cohere_model: str
    bedrock_claude_model: str

    log_level: str = "INFO"

    class Config:
        env_file = None

def load_settings() -> Settings:
    env = os.getenv("ENVIRONMENT", "dev")
    env_file = f"env/.env.{env}"
    if os.path.exists(env_file):
        load_dotenv(env_file)
    else:
        load_dotenv()  # fallback: .env at root if someone uses it locally

    return Settings(
        environment=os.getenv("ENVIRONMENT", "dev"),
        aws_region=os.getenv("AWS_REGION", "us-east-1"),
        opensearch_endpoint=os.getenv("OPENSEARCH_ENDPOINT", ""),
        opensearch_index=os.getenv("OPENSEARCH_INDEX", "rag_documents"),
        bedrock_cohere_model=os.getenv("BEDROCK_COHERE_MODEL", ""),
        bedrock_claude_model=os.getenv("BEDROCK_CLAUDE_MODEL", ""),
        log_level=os.getenv("LOG_LEVEL", "INFO"),
    )

settings = load_settings()

