import logging
from typing import List, Dict, Any, Optional
from backend.utils.cosmos_db import get_cosmos_db_client
from backend.utils.logger import get_logger

# Set up logger
logger = get_logger(__name__)

class CosmosDBExtensions:
    """Extensions for the CosmosDBClient to support vector search."""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one instance of the helper is created."""
        if cls._instance is None:
            cls._instance = super(CosmosDBExtensions, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the CosmosDBExtensions."""
        if self._initialized:
            return
            
        logger.info("Initializing CosmosDBExtensions")
        
        # Get the CosmosDBClient
        self.cosmos_client = get_cosmos_db_client()
        
        self._initialized = True
        logger.info("CosmosDBExtensions initialized successfully")
    
    async def query_sources(self, query: str, parameters: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Execute a custom query on the sources container.
        
        Args:
            query (str): The query to execute.
            parameters (List[Dict[str, Any]], optional): Query parameters. Defaults to None.
            
        Returns:
            List[Dict[str, Any]]: The query results.
        """
        try:
            logger.info(f"Executing query on sources container: {query}")
            
            # Get the container client
            container = self.cosmos_client.sources_container
            
            # Execute the query
            if parameters:
                items = list(container.query_items(
                    query=query,
                    parameters=parameters,
                    enable_cross_partition_query=True
                ))
            else:
                items = list(container.query_items(
                    query=query,
                    enable_cross_partition_query=True
                ))
            
            logger.info(f"Query returned {len(items)} items")
            return items
        
        except Exception as e:
            logger.error(f"Error executing query on sources container: {str(e)}", exc_info=True)
            raise
    
    async def query_pages(self, query: str, parameters: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Execute a custom query on the pages container.
        
        Args:
            query (str): The query to execute.
            parameters (List[Dict[str, Any]], optional): Query parameters. Defaults to None.
            
        Returns:
            List[Dict[str, Any]]: The query results.
        """
        try:
            logger.info(f"Executing query on pages container: {query}")
            
            # Get the container client
            container = self.cosmos_client.pages_container
            
            # Execute the query
            if parameters:
                items = list(container.query_items(
                    query=query,
                    parameters=parameters,
                    enable_cross_partition_query=True
                ))
            else:
                items = list(container.query_items(
                    query=query,
                    enable_cross_partition_query=True
                ))
            
            logger.info(f"Query returned {len(items)} items")
            return items
        
        except Exception as e:
            logger.error(f"Error executing query on pages container: {str(e)}", exc_info=True)
            raise

# Create a singleton instance
cosmos_db_extensions = None

def get_cosmos_db_extensions() -> CosmosDBExtensions:
    """Get or create the CosmosDBExtensions singleton."""
    global cosmos_db_extensions
    if cosmos_db_extensions is None:
        cosmos_db_extensions = CosmosDBExtensions()
    return cosmos_db_extensions
