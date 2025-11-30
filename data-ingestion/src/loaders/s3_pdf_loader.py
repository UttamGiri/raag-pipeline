import io, os, boto3
from pypdf import PdfReader
from src.utils.logger import get_logger

logger = get_logger(__name__)

def read_pdf_from_s3(bucket: str, key: str) -> str:
    s3 = boto3.client("s3", region_name=os.getenv("AWS_REGION"))
    logger.info(f"Downloading s3://{bucket}/{key}")

    data = s3.get_object(Bucket=bucket, Key=key)["Body"].read()
    reader = PdfReader(io.BytesIO(data))

    text = [(page.extract_text() or "") for page in reader.pages]
    return "\n\n".join(text)

