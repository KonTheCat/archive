from azure.identity import DefaultAzureCredential
from azure.mgmt.storage import StorageManagementClient
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Get environment variables
STORAGE_ACCOUNT_NAME = os.environ.get("STORAGE_ACCOUNT_NAME")
STORAGE_CONTAINER_NAME = os.environ.get("STORAGE_CONTAINER_NAME")
SUBSCRIPTION_ID = os.environ.get("SUBSCRIPTION_ID")
RG_NAME = os.environ.get("RG_NAME")

def ensure_container_exists():
    """Ensure that the blob storage container exists."""
    logger.info(f"Ensuring blob storage container exists: {STORAGE_CONTAINER_NAME}")
    
    try:
        # Create credential
        credential = DefaultAzureCredential()
        
        # Create storage management client
        storage_client = StorageManagementClient(
            credential=credential,
            subscription_id=SUBSCRIPTION_ID
        )
        
        # Get the storage account keys
        keys = storage_client.storage_accounts.list_keys(
            resource_group_name=RG_NAME,
            account_name=STORAGE_ACCOUNT_NAME
        )
        
        # Get the storage account connection string
        from azure.storage.blob import BlobServiceClient
        
        # Create blob service client using DefaultAzureCredential
        account_url = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net"
        blob_service_client = BlobServiceClient(
            account_url=account_url,
            credential=credential
        )
        
        # Check if container exists
        container_client = blob_service_client.get_container_client(STORAGE_CONTAINER_NAME)
        
        try:
            container_properties = container_client.get_container_properties()
            logger.info(f"Container already exists: {STORAGE_CONTAINER_NAME}")
        except Exception:
            # Create container if it doesn't exist
            logger.info(f"Container not found. Creating: {STORAGE_CONTAINER_NAME}")
            container_client.create_container()
            logger.info(f"Container created successfully: {STORAGE_CONTAINER_NAME}")
        
    except Exception as e:
        logger.error(f"Error ensuring blob storage container exists: {str(e)}")
        raise

def main():
    """Main function to set up the blob storage container."""
    logger.info("Starting blob storage container setup for Archive application")
    
    try:
        ensure_container_exists()
        logger.info("Blob storage container setup completed successfully")
    
    except Exception as e:
        logger.error(f"Error setting up blob storage container: {str(e)}")
        raise

if __name__ == "__main__":
    main()
