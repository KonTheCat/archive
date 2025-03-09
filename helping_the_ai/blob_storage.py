import os
import logging
import uuid
from typing import Dict, Any, Optional, BinaryIO
from azure.storage.blob import BlobServiceClient, ContentSettings
from azure.identity import DefaultAzureCredential

# Get logger for this module
logger = logging.getLogger(__name__)


class BlobStorageClient:
    """Client for interacting with Azure Blob Storage."""

    def __init__(self):
        """Initialize the Blob Storage client using environment variables."""
        logger.info("Initializing BlobStorageClient")

        # Get environment variables
        self.storage_account_name = os.environ.get("STORAGE_ACCOUNT_NAME")

        logger.info("Storage account name: %s", self.storage_account_name)

        # Validate environment variables
        if not self.storage_account_name:
            logger.error(
                "Missing required environment variable: STORAGE_ACCOUNT_NAME")
            raise ValueError(
                "STORAGE_ACCOUNT_NAME environment variable must be set")

        try:
            # Create a credential using DefaultAzureCredential
            logger.info("Creating DefaultAzureCredential")
            self.credential = DefaultAzureCredential()

            # Create the BlobServiceClient
            logger.info("Creating BlobServiceClient")
            account_url = f"https://{self.storage_account_name}.blob.core.windows.net"
            self.client = BlobServiceClient(
                account_url=account_url, credential=self.credential)

            # Ensure container exists
            logger.info("Ensuring container exists")
            self._ensure_container_exists()

            logger.info(
                "BlobStorageClient initialization completed successfully")

        except Exception as e:
            logger.error("Error initializing BlobStorageClient: %s",
                         str(e), exc_info=True)
            raise

    def _ensure_container_exists(self):
        """Ensure that the required container exists."""
        container_name = "spaces-files"

        try:
            # Check if container exists
            logger.info("Checking if container exists: %s", container_name)
            container_client = self.client.get_container_client(container_name)
            container_client.get_container_properties()
            logger.info("Container '%s' already exists", container_name)
        except Exception as e:
            # Create container if it doesn't exist
            logger.info("Container '%s' not found. Creating it...",
                        container_name)
            logger.debug("Error when checking for container: %s", str(e))

            try:
                self.client.create_container(container_name)
                logger.info("Container '%s' created successfully",
                            container_name)
            except Exception as create_error:
                logger.error("Failed to create container '%s': %s",
                             container_name, str(create_error), exc_info=True)
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
        logger.info("Uploading file: %s", file_name)

        try:
            # Generate a unique blob name
            file_extension = os.path.splitext(file_name)[1]
            blob_name = f"{uuid.uuid4()}{file_extension}"
            container_name = "spaces-files"

            # Get container client
            container_client = self.client.get_container_client(container_name)

            # Get blob client
            blob_client = container_client.get_blob_client(blob_name)

            # Set content settings
            content_settings = ContentSettings(content_type=content_type)

            # Upload the file
            file.seek(0)  # Ensure we're at the beginning of the file
            blob_client.upload_blob(file, content_settings=content_settings)

            # Get the blob URL
            blob_url = blob_client.url

            logger.info("File uploaded successfully: %s", blob_url)

            return {
                "url": blob_url,
                "name": file_name,
                "blob_name": blob_name,
                "content_type": content_type,
                "container": container_name
            }

        except Exception as e:
            logger.error("Error uploading file: %s", str(e), exc_info=True)
            raise

    async def delete_file(self, blob_name: str) -> None:
        """
        Delete a file from blob storage.

        Args:
            blob_name: The name of the blob to delete
        """
        logger.info("Deleting file: %s", blob_name)

        try:
            container_name = "spaces-files"

            # Get container client
            container_client = self.client.get_container_client(container_name)

            # Get blob client
            blob_client = container_client.get_blob_client(blob_name)

            # Delete the blob
            blob_client.delete_blob()

            logger.info("File deleted successfully: %s", blob_name)

        except Exception as e:
            logger.error("Error deleting file: %s", str(e), exc_info=True)
            raise


# Create a singleton instance
blob_storage_client = None


def get_blob_storage_client() -> BlobStorageClient:
    """Get or create the BlobStorageClient singleton."""
    global blob_storage_client
    if blob_storage_client is None:
        blob_storage_client = BlobStorageClient()
    return blob_storage_client
