import os
import re
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from azure.cosmos import CosmosClient
from azure.identity import DefaultAzureCredential

from backend.utils.logger import get_logger

# Set up logger
logger = get_logger(__name__)

class CosmosDBClient:
    """Client for interacting with Azure Cosmos DB."""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one instance of the client is created."""
        if cls._instance is None:
            cls._instance = super(CosmosDBClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the Cosmos DB client using environment variables."""
        if self._initialized:
            return
            
        logger.info("Initializing CosmosDBClient")
        
        # Get environment variables
        self.cosmos_url = os.environ.get("COSMOS_DB_URL")
        self.database_name = os.environ.get("COSMOS_DB_DATABASE")
        
        # Validate environment variables
        if not self.cosmos_url or not self.database_name:
            logger.error("Missing required environment variables: COSMOS_DB_URL or COSMOS_DB_DATABASE")
            raise ValueError("COSMOS_DB_URL and COSMOS_DB_DATABASE environment variables must be set")
        
        try:
            # Create a credential using DefaultAzureCredential
            logger.info("Creating DefaultAzureCredential")
            self.credential = DefaultAzureCredential()
            
            # Initialize the Cosmos DB client
            logger.info("Initializing CosmosClient")
            self.client = CosmosClient(self.cosmos_url, credential=self.credential)
            
            # Get database client
            logger.info(f"Getting database client for: {self.database_name}")
            self.database = self.client.get_database_client(self.database_name)
            
            # Define container names
            self.sources_container_name = "sources"
            self.pages_container_name = "pages"
            
            # Get container clients
            logger.info(f"Getting container client for: {self.sources_container_name}")
            self.sources_container = self.database.get_container_client(self.sources_container_name)
            
            logger.info(f"Getting container client for: {self.pages_container_name}")
            self.pages_container = self.database.get_container_client(self.pages_container_name)
            
            self._initialized = True
            logger.info("CosmosDBClient initialization completed successfully")
            
        except Exception as e:
            logger.error(f"Error initializing CosmosDBClient: {str(e)}", exc_info=True)
            raise
    
    # Source Operations (previously spaces)
    
    async def get_sources(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all sources, optionally filtered by user_id."""
        logger.info("Getting sources")
        
        if user_id:
            query = f"SELECT * FROM c WHERE c.userId = '{user_id}' ORDER BY c.updatedAt DESC"
            logger.info(f"Executing query for user {user_id}: {query}")
        else:
            query = "SELECT * FROM c ORDER BY c.updatedAt DESC"
            logger.info(f"Executing query for all users: {query}")
        
        try:
            items = list(self.sources_container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            logger.info(f"Retrieved {len(items)} sources")
            return items
        except Exception as e:
            logger.error(f"Error getting sources: {str(e)}", exc_info=True)
            raise
    
    async def get_source(self, source_id: str) -> Optional[Dict[str, Any]]:
        """Get a source by ID."""
        try:
            return self.sources_container.read_item(
                item=source_id,
                partition_key=source_id
            )
        except Exception:
            return None
    
    async def create_source(self, source: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new source."""
        logger.info(f"Creating source: id={source.get('id', 'unknown')}, name={source.get('name', 'unknown')}")
        
        # Convert datetime objects to ISO format strings
        if 'createdAt' in source and isinstance(source['createdAt'], datetime):
            source['createdAt'] = source['createdAt'].isoformat()
        if 'updatedAt' in source and isinstance(source['updatedAt'], datetime):
            source['updatedAt'] = source['updatedAt'].isoformat()
        
        try:
            result = self.sources_container.create_item(body=source)
            logger.info(f"Source created successfully: id={result.get('id', 'unknown')}, name={result.get('name', 'unknown')}")
            return result
        except Exception as e:
            logger.error(f"Error creating source: {str(e)}", exc_info=True)
            raise
    
    async def update_source(self, source_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing source."""
        # Get the current source
        source = await self.get_source(source_id)
        if not source:
            raise ValueError(f"Source with ID {source_id} not found")
        
        # Convert datetime objects to ISO format strings
        for key, value in updates.items():
            if isinstance(value, datetime):
                updates[key] = value.isoformat()
        
        # Update the source with the new values
        for key, value in updates.items():
            source[key] = value
        
        # Save the updated source
        return self.sources_container.replace_item(
            item=source_id,
            body=source
        )
    
    async def delete_source(self, source_id: str) -> None:
        """Delete a source and all its pages."""
        # Delete the source
        self.sources_container.delete_item(
            item=source_id,
            partition_key=source_id
        )
        
        # Delete all pages for this source
        query = f"SELECT * FROM c WHERE c.sourceId = '{source_id}'"
        pages = list(self.pages_container.query_items(
            query=query,
            partition_key=source_id
        ))
        
        for page in pages:
            self.pages_container.delete_item(
                item=page['id'],
                partition_key=source_id
            )
    
    # Page Operations (previously space_documents)
    
    async def get_pages(self, source_id: str) -> List[Dict[str, Any]]:
        """Get all pages for a source."""
        logger.info(f"Getting pages for source ID: {source_id}")
        
        query = f"SELECT * FROM c WHERE c.sourceId = '{source_id}' ORDER BY c.updatedAt DESC"
        logger.info(f"Executing query: {query}")
        
        try:
            items = list(self.pages_container.query_items(
                query=query,
                partition_key=source_id
            ))
            logger.info(f"Retrieved {len(items)} pages for source {source_id}")
            return items
        except Exception as e:
            logger.error(f"Error getting pages: {str(e)}", exc_info=True)
            raise
    
    async def get_page(self, source_id: str, page_id: str) -> Optional[Dict[str, Any]]:
        """Get a page by ID."""
        try:
            return self.pages_container.read_item(
                item=page_id,
                partition_key=source_id
            )
        except Exception:
            return None
    
    async def create_page(self, page: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new page."""
        logger.info(f"Creating page: id={page.get('id', 'unknown')}, sourceId={page.get('sourceId', 'unknown')}")
        
        # Ensure the page has a sourceId for partitioning
        if 'sourceId' not in page:
            logger.error(f"Page missing sourceId: {page}")
            raise ValueError("Page must have a sourceId")
        
        # Convert datetime objects to ISO format strings
        if 'createdAt' in page and isinstance(page['createdAt'], datetime):
            page['createdAt'] = page['createdAt'].isoformat()
        if 'updatedAt' in page and isinstance(page['updatedAt'], datetime):
            page['updatedAt'] = page['updatedAt'].isoformat()
        
        try:
            result = self.pages_container.create_item(body=page)
            logger.info(f"Page created successfully: id={result.get('id', 'unknown')}")
            return result
        except Exception as e:
            logger.error(f"Error creating page: {str(e)}", exc_info=True)
            raise
    
    async def update_page(self, source_id: str, page_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing page."""
        # Get the current page
        page = await self.get_page(source_id, page_id)
        if not page:
            raise ValueError(f"Page with ID {page_id} not found in source {source_id}")
        
        # Convert datetime objects to ISO format strings
        for key, value in updates.items():
            if isinstance(value, datetime):
                updates[key] = value.isoformat()
        
        # Update the page with the new values
        for key, value in updates.items():
            page[key] = value
        
        # Save the updated page
        return self.pages_container.replace_item(
            item=page_id,
            body=page
        )
    
    async def delete_page(self, source_id: str, page_id: str) -> None:
        """Delete a page."""
        self.pages_container.delete_item(
            item=page_id,
            partition_key=source_id
        )

# Create a singleton instance
cosmos_db_client = None

def get_cosmos_db_client() -> CosmosDBClient:
    """Get or create the CosmosDBClient singleton."""
    global cosmos_db_client
    if cosmos_db_client is None:
        cosmos_db_client = CosmosDBClient()
    return cosmos_db_client
