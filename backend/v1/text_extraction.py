import os
import logging
import datetime
import tempfile
import aiohttp
import asyncio
from fastapi import BackgroundTasks
from azure.storage.blob import BlobServiceClient

from backend.utils.document_intelligence import get_document_intelligence_helper
from backend.utils.blob_storage import get_blob_storage_client
from backend.utils.cosmos_db import get_cosmos_db_client
from backend.utils.logger import get_logger
from backend.utils.vector_embeddings import get_vector_embeddings_helper

# Set up logger
logger = get_logger(__name__)

# Create a separate logger for text extraction tasks
extraction_logger = logging.getLogger("text_extraction")
extraction_logger.setLevel(logging.INFO)

# Check if running in local development
is_local_dev = os.environ.get('WEBSITE_SITE_NAME') is None

# If in local development, set up a file handler for the extraction log
if is_local_dev:
    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # Create a file handler for the extraction log
    extraction_log_file = f"{logs_dir}/text_extraction.log"
    file_handler = logging.FileHandler(extraction_log_file)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    extraction_logger.addHandler(file_handler)
    
    # Log that extraction logging is enabled
    extraction_logger.info("Text extraction logging enabled in local development mode")

async def download_blob_to_temp_file(blob_url):
    """
    Download a blob from a URL to a temporary file.
    
    Args:
        blob_url (str): URL of the blob to download.
        
    Returns:
        str: Path to the temporary file.
    """
    try:
        # Create a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        temp_file_path = temp_file.name
        temp_file.close()
        
        # Download the blob
        async with aiohttp.ClientSession() as session:
            async with session.get(blob_url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to download blob: {response.status}")
                
                with open(temp_file_path, "wb") as f:
                    f.write(await response.read())
        
        logger.info(f"Downloaded blob to temporary file: {temp_file_path}")
        return temp_file_path
    
    except Exception as e:
        logger.error(f"Error downloading blob: {str(e)}", exc_info=True)
        raise

async def extract_text_from_blob(blob_url, source_id, page_id):
    """
    Extract text from a blob and update the page document in Cosmos DB.
    This function is intended to be run as a background task.
    
    Args:
        blob_url (str): URL of the blob to extract text from.
        source_id (str): ID of the source.
        page_id (str): ID of the page.
    """
    start_time = datetime.datetime.now()
    extraction_logger.info(f"Starting text extraction for page {page_id} in source {source_id}")
    
    try:
        # Get the document intelligence helper
        doc_intelligence = get_document_intelligence_helper()
        
        # Get the Cosmos DB client
        cosmos_client = get_cosmos_db_client()
        
        # Get the vector embeddings helper
        vector_embeddings = get_vector_embeddings_helper()
        
        # Check if the page still exists before proceeding
        page = await cosmos_client.get_page(source_id, page_id)
        if not page:
            extraction_logger.warning(
                f"Page {page_id} in source {source_id} not found. Skipping text extraction."
            )
            return
        
        # Download the blob to a temporary file
        temp_file_path = await download_blob_to_temp_file(blob_url)
        
        try:
            # Extract text from the image
            extracted_text = await doc_intelligence.extract_text_from_image(temp_file_path)
            
            # Generate vector embeddings for the extracted text
            extraction_logger.info(f"Generating vector embeddings for page {page_id}")
            content_vector = await vector_embeddings.get_embeddings(extracted_text)
            
            # Check again if the page still exists before updating
            page = await cosmos_client.get_page(source_id, page_id)
            if not page:
                extraction_logger.warning(
                    f"Page {page_id} in source {source_id} was deleted during text extraction. Skipping update."
                )
                return
            
            # Update the page document in Cosmos DB
            update_data = {
                "extractedText": extracted_text,
                "contentVector": content_vector,
                "updatedAt": datetime.datetime.now().isoformat()
            }
            
            await cosmos_client.update_page(source_id, page_id, update_data)
            
            end_time = datetime.datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            extraction_logger.info(
                f"Completed text extraction and vector embedding for page {page_id} in source {source_id}. "
                f"Duration: {duration:.2f} seconds. "
                f"Extracted {len(extracted_text)} characters. "
                f"Vector dimensions: {len(content_vector)}."
            )
            
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                logger.info(f"Deleted temporary file: {temp_file_path}")
    
    except Exception as e:
        extraction_logger.error(
            f"Error extracting text for page {page_id} in source {source_id}: {str(e)}",
            exc_info=True
        )

def schedule_text_extraction(background_tasks, blob_url, source_id, page_id):
    """
    Schedule text extraction as a background task.
    
    Args:
        background_tasks (BackgroundTasks): FastAPI BackgroundTasks instance.
        blob_url (str): URL of the blob to extract text from.
        source_id (str): ID of the source.
        page_id (str): ID of the page.
    """
    logger.info(f"Scheduling text extraction for page {page_id} in source {source_id}")
    background_tasks.add_task(extract_text_from_blob, blob_url, source_id, page_id)
