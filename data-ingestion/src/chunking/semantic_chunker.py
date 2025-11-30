import os
from langchain_text_splitters import SemanticChunker
from src.embeddings.cohere_bedrock_embeddings import CohereBedrockEmbedder
from src.utils.logger import get_logger

logger = get_logger(__name__)

def semantic_split(
    text: str,
    embeddings=None,
    max_chunk_size: int = None,
    min_chunk_size: int = None,
    breakpoint_threshold_type: str = None
):
    """
    Split text into semantic chunks using Cohere Bedrock embeddings.
    
    Args:
        text: Text to split
        embeddings: Embedding model (defaults to CohereBedrockEmbedder)
        max_chunk_size: Maximum size of each chunk in characters (default: 1000 or from env)
        min_chunk_size: Minimum size of each chunk in characters (default: 200 or from env)
        breakpoint_threshold_type: Type of threshold for breakpoints 
            ("percentile", "standard_deviation", or "interquartile")
            (default: "percentile" or from env)
    
    Returns:
        List of text chunks
    """
    if embeddings is None:
        embeddings = CohereBedrockEmbedder()
        logger.info("Using Cohere Bedrock embeddings for semantic chunking")
    
    # Get parameters from environment or use defaults
    max_chunk = max_chunk_size or int(os.getenv("MAX_CHUNK_SIZE", "1000"))
    min_chunk = min_chunk_size or int(os.getenv("MIN_CHUNK_SIZE", "200"))
    breakpoint_type = breakpoint_threshold_type or os.getenv("BREAKPOINT_THRESHOLD_TYPE", "percentile")
    
    splitter = SemanticChunker(
        embeddings=embeddings,
        max_chunk_size=max_chunk,
        min_chunk_size=min_chunk,
        breakpoint_threshold_type=breakpoint_type
    )
    
    chunks = splitter.split_text(text)
    logger.info(f"Split text into {len(chunks)} semantic chunks (max={max_chunk}, min={min_chunk}, threshold={breakpoint_type})")
    return chunks

