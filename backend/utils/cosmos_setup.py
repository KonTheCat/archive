from azure.identity import DefaultAzureCredential
from azure.mgmt.cosmosdb import CosmosDBManagementClient
import os
import re
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get environment variables
COSMOS_DB_URL = os.environ.get("COSMOS_DB_URL")
COSMOS_DB_DATABASE = os.environ.get("COSMOS_DB_DATABASE")
SUBSCRIPTION_ID = os.environ.get("SUBSCRIPTION_ID")
RG_NAME = os.environ.get("RESOURCE_GROUP", os.environ.get("RG_NAME"))
LOCATION = os.environ.get("LOCATION")

# Extract account name from URL (e.g., https://konthecat.documents.azure.com:443/)
account_match = re.match(r'https://([^.]+)\.documents\.azure\.com', COSMOS_DB_URL)
if not account_match:
    raise ValueError(f"Invalid Cosmos DB URL format: {COSMOS_DB_URL}")

COSMOSDB_ACCOUNT_NAME = account_match.group(1)

# Define container names
SOURCES_CONTAINER_NAME = "sources"
PAGES_CONTAINER_NAME = "pages"

# Define indexing policy for sources container
sources_indexing_policy = {
    "includedPaths": [
        {
            "path": "/*"
        }
    ],
    "excludedPaths": [
        {
            "path": "/\"_etag\"/?"
        }
    ]
}

# Define indexing policy for pages container with full-text search capabilities
pages_indexing_policy = {
    "includedPaths": [
        {
            "path": "/*"
        }
    ],
    "excludedPaths": [
        {
            "path": "/\"_etag\"/?"
        },
        {
            "path": "/contentVector/*"
        }
    ],
    "compositeIndexes": [
        [
            {
                "path": "/spaceId",
                "order": "ascending"
            },
            {
                "path": "/createdAt",
                "order": "descending"
            }
        ]
    ],
    "vectorIndexes": [
        {
            "path": "/contentVector",
            "type": "quantizedFlat"
        }
    ]
}

# Define full-text search policy for pages
pages_full_text_policy = {
    "defaultLanguage": "en-US",
    "fullTextPaths": [
        {
            "path": "/extractedText",
            "language": "en-US"
        },
        {
            "path": "/notes",
            "language": "en-US"
        }
    ]
}

# Define vector embedding policy for pages
pages_vector_embedding_policy = {
    "vectorEmbeddings": [
        {
            "path": "/contentVector",
            "dataType": "float32",
            "distanceFunction": "cosine",
            "dimensions": 3072  # text-embedding-3-large has 3072 dimensions
        }
    ]
}

def container_exists(management_client, container_name):
    """Check if a container exists."""
    try:
        management_client.sql_resources.get_sql_container(
            resource_group_name=RG_NAME,
            account_name=COSMOSDB_ACCOUNT_NAME,
            database_name=COSMOS_DB_DATABASE,
            container_name=container_name
        )
        return True
    except Exception:
        return False

def create_container(management_client, container_name, partition_key_path, indexing_policy, full_text_policy=None, vector_embedding_policy=None):
    """Create a container with the specified configuration."""
    logger = logging.getLogger(__name__)
    logger.info(f"Creating container: {container_name}")
    
    # Define container parameters
    container_parameters = {
        "location": LOCATION,
        "resource": {
            "id": container_name,
            "indexing_policy": indexing_policy,
            "partition_key": {
                "paths": [
                    partition_key_path
                ]
            }
        }
    }
    
    # Add full-text policy if provided
    if full_text_policy:
        container_parameters["resource"]["full_text_policy"] = full_text_policy
        
    # Add vector embedding policy if provided
    if vector_embedding_policy:
        container_parameters["resource"]["vector_embedding_policy"] = vector_embedding_policy
    
    try:
        # Create or update the container
        container = management_client.sql_resources.begin_create_update_sql_container(
            resource_group_name=RG_NAME,
            account_name=COSMOSDB_ACCOUNT_NAME,
            database_name=COSMOS_DB_DATABASE,
            container_name=container_name,
            create_update_sql_container_parameters=container_parameters
        ).result()
        
        logger.info(f"Container created successfully: {container_name}")
        return container
    except Exception as e:
        logger.error(f"Error creating container {container_name}: {str(e)}")
        raise

def ensure_container_exists(management_client, container_name, partition_key_path, indexing_policy, full_text_policy=None, vector_embedding_policy=None):
    """Ensure that a container exists, create it if it doesn't."""
    logger = logging.getLogger(__name__)
    logger.info(f"Ensuring container exists: {container_name}")
    
    if container_exists(management_client, container_name):
        logger.info(f"Container already exists: {container_name}")
        return True
    else:
        logger.info(f"Container not found. Creating: {container_name}")
        create_container(management_client, container_name, partition_key_path, indexing_policy, full_text_policy, vector_embedding_policy)
        return True

def ensure_database_exists(management_client):
    """Ensure that the database exists, create it if it doesn't."""
    logger = logging.getLogger(__name__)
    logger.info(f"Ensuring database exists: {COSMOS_DB_DATABASE}")
    
    try:
        # Check if database exists
        management_client.sql_resources.get_sql_database(
            resource_group_name=RG_NAME,
            account_name=COSMOSDB_ACCOUNT_NAME,
            database_name=COSMOS_DB_DATABASE
        )
        logger.info(f"Database already exists: {COSMOS_DB_DATABASE}")
    except Exception:
        # Create database if it doesn't exist
        logger.info(f"Database not found. Creating: {COSMOS_DB_DATABASE}")
        
        database_params = {
            "resource": {
                "id": COSMOS_DB_DATABASE
            }
        }
        
        management_client.sql_resources.begin_create_update_sql_database(
            resource_group_name=RG_NAME,
            account_name=COSMOSDB_ACCOUNT_NAME,
            database_name=COSMOS_DB_DATABASE,
            create_update_sql_database_parameters=database_params
        ).result()
        
        logger.info(f"Database created successfully: {COSMOS_DB_DATABASE}")

def setup_cosmos_containers():
    """Main function to set up the Cosmos DB containers."""
    logger = logging.getLogger(__name__)
    logger.info("Starting Cosmos DB container setup for Archive application")
    
    try:
        # Create credential
        credential = DefaultAzureCredential()
        
        # Create management client
        management_client = CosmosDBManagementClient(
            credential=credential,
            subscription_id=SUBSCRIPTION_ID
        )
        
        # Ensure database exists
        ensure_database_exists(management_client)
        
        # Ensure sources container (spaces) exists
        ensure_container_exists(
            management_client,
            SOURCES_CONTAINER_NAME,
            "/id",
            sources_indexing_policy
        )
        
        # Ensure pages container (space_documents) exists
        ensure_container_exists(
            management_client,
            PAGES_CONTAINER_NAME,
            "/spaceId",
            pages_indexing_policy,
            pages_full_text_policy,
            pages_vector_embedding_policy
        )
        
        logger.info("Cosmos DB container setup completed successfully")
    
    except Exception as e:
        logger.error(f"Error setting up Cosmos DB containers: {str(e)}")
        raise

if __name__ == "__main__":
    # Set up logger for standalone execution
    logging.basicConfig(level=logging.INFO)
    setup_cosmos_containers()
