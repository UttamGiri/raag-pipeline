# data-ingestion/admin/reingest_document.py

import typer
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ensure we can import from admin directory
admin_dir = Path(__file__).parent
if str(admin_dir) not in sys.path:
    sys.path.insert(0, str(admin_dir.parent))

from admin.delete_chunks import delete as delete_chunks
from src.pipelines.ingestion_pipeline import run_pipeline
from src.utils.logger import get_logger

app = typer.Typer(help="Delete old chunks and re-ingest PDF")
logger = get_logger(__name__)

def load_env():
    """Load environment variables from .env file."""
    env = os.getenv("ENVIRONMENT", "dev")
    env_file = f"env/.env.{env}"
    
    if os.path.exists(env_file):
        load_dotenv(env_file)
    else:
        load_dotenv()  # Fallback to default .env if exists

@app.command()
def reingest(bucket: str, key: str):
    """
    Deletes old chunks and re-runs ingestion for one PDF.
    Uses the same chunking, embedding, PII, and hashing logic as the main pipeline.
    """
    
    load_env()
    
    typer.echo("\nStep 1 — Delete previous chunks:")
    try:
        delete_chunks(bucket=bucket, key=key)
    except typer.Abort:
        typer.echo("Deletion cancelled. Aborting re-ingestion.")
        raise
    
    typer.echo("\nStep 2 — Re-ingesting document with existing ingestion pipeline...")
    
    # Set environment variables for the pipeline
    os.environ["S3_BUCKET_NAME"] = bucket
    os.environ["S3_PDF_KEY"] = key
    
    logger.info(f"Starting re-ingestion for s3://{bucket}/{key}")
    
    try:
        # Reuse existing ingestion pipeline
        run_pipeline()
        typer.secho("\n✓ Re-ingestion completed successfully!", fg="green")
        logger.info(f"Successfully re-ingested s3://{bucket}/{key}")
    except Exception as e:
        typer.secho(f"\n✗ Re-ingestion failed: {str(e)}", fg="red")
        logger.error(f"Re-ingestion failed for s3://{bucket}/{key}: {str(e)}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()

