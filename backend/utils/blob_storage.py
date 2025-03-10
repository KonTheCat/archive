import os
import logging
import uuid
from typing import Dict, Any, BinaryIO
from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.identity import DefaultAzureCredential

from backend.utils.logger import get_logger

# Set up logger
logger = get_logger(__name__)

class BlobStorageClient:
    """Client for interacting with Azure Blob Storage."""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one instance of the client is created."""
        if cls._instance is None:
            cls._instance = super(BlobStorageClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the Blob Storage client using environment variables."""
        if self._initialized:
            return
            
        logger.info("Initializing BlobStorageClient")
        
        # Get environment variables
        self.storage_account_name = os.environ.get("STORAGE_ACCOUNT_NAME")
        self.container_name = os.environ.get("STORAGE_CONTAINER_NAME")
        
        # Validate environment variables
        if not self.storage_account_name:
            logger.error("Missing required environment variable: STORAGE_ACCOUNT_NAME")
            raise ValueError("STORAGE_ACCOUNT_NAME environment variable must be set")
        
        if not self.container_name:
            logger.error("Missing required environment variable: STORAGE_CONTAINER_NAME")
            raise ValueError("STORAGE_CONTAINER_NAME environment variable must be set")
        
        try:
            # Create a credential using DefaultAzureCredential
            logger.info("Creating DefaultAzureCredential")
            self.credential = DefaultAzureCredential()
            
            # Create the BlobServiceClient
            logger.info("Creating BlobServiceClient")
            account_url = f"https://{self.storage_account_name}.blob.core.windows.net"
            self.client = BlobServiceClient(account_url=account_url, credential=self.credential)
            
            # Ensure container exists
            logger.info("Ensuring container exists")
            self._ensure_container_exists()
            
            self._initialized = True
            logger.info("BlobStorageClient initialization completed successfully")
            
        except Exception as e:
            logger.error(f"Error initializing BlobStorageClient: {str(e)}", exc_info=True)
            raise
    
    def _ensure_container_exists(self):
        """Ensure that the required container exists."""
        try:
            # Check if container exists
            logger.info(f"Checking if container exists: {self.container_name}")
            container_client = self.client.get_container_client(self.container_name)
            container_client.get_container_properties()
            logger.info(f"Container '{self.container_name}' already exists")
        except Exception as e:
            # Create container if it doesn't exist
            logger.info(f"Container '{self.container_name}' not found. Creating it...")
            logger.debug(f"Error when checking for container: {str(e)}")
            
            try:
                self.client.create_container(self.container_name)
                logger.info(f"Container '{self.container_name}' created successfully")
            except Exception as create_error:
                logger.error(f"Failed to create container '{self.container_name}': {str(create_error)}", exc_info=True)
                raise
    
    async def upload_file(self, file: BinaryIO, file_name: str, content_type: str) -> Dict[str, Any]:
        """
        Upload a file to blob storage.
        
        Args:
            file: The file-like object to upload
            file_name: Original file name
            content_type: MIME type of the file
            
        Returns:
            Dict with file metadata including URL
        """
        logger.info(f"Uploading file: {file_name}")
        
        try:
            # Generate a unique blob name
            file_extension = os.path.splitext(file_name)[1]
            blob_name = f"{uuid.uuid4()}{file_extension}"
            
            # Get container client
            container_client = self.client.get_container_client(self.container_name)
            
            # Get blob client
            blob_client = container_client.get_blob_client(blob_name)
            
            # Set content settings
            content_settings = ContentSettings(content_type=content_type)
            
            # Upload the file
            file.seek(0)  # Ensure we're at the beginning of the file
            blob_client.upload_blob(file, content_settings=content_settings)
            
            # Get the blob URL
            blob_url = blob_client.url
            
            logger.info(f"File uploaded successfully: {blob_url}")
            
            return {
                "url": blob_url,
                "name": file_name,
                "blob_name": blob_name,
                "content_type": content_type,
                "container": self.container_name
            }
            
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}", exc_info=True)
            raise
    
    async def delete_file(self, blob_name: str) -> None:
        """
        Delete a file from blob storage.
        
        Args:
            blob_name: The name of the blob to delete
        """
        logger.info(f"Deleting file: {blob_name}")
        
        try:
            # Get container client
            container_client = self.client.get_container_client(self.container_name)
            
            # Get blob client
            blob_client = container_client.get_blob_client(blob_name)
            
            # Delete the blob
            blob_client.delete_blob()
            
            logger.info(f"File deleted successfully: {blob_name}")
            
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}", exc_info=True)
            raise

# Create a singleton instance
blob_storage_client = None

def get_blob_storage_client() -> BlobStorageClient:
    """Get or create the BlobStorageClient singleton."""
    global blob_storage_client
    if blob_storage_client is None:
        blob_storage_client = BlobStorageClient()
    return blob_storage_client
