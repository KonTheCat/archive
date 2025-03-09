import os
import logging
from typing import List
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI
import httpx

# Get logger for this module
from backend.utils.logger import get_logger
logger = get_logger(__name__)

class VectorEmbeddingsHelper:
    """Helper class for generating vector embeddings using Azure OpenAI API."""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one instance of the helper is created."""
        if cls._instance is None:
            cls._instance = super(VectorEmbeddingsHelper, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the Azure OpenAI client."""
        if self._initialized:
            return
            
        logger.info("Initializing VectorEmbeddingsHelper")
        
        # Get environment variables
        self.api_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        self.api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-06-01")
        self.embedding_deployment = os.environ.get("AOAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large")
        
        # Initialize the client
        try:
            # Use DefaultAzureCredential for authentication (identity-based auth)
            logger.info("Using DefaultAzureCredential for authentication")
            credential = DefaultAzureCredential()
            
            # Create a token provider for Azure OpenAI
            token_provider = get_bearer_token_provider(
                credential, "https://cognitiveservices.azure.com/.default"
            )
            
            # Create a custom HTTP client without proxies
            http_client = httpx.Client()
            
            # Create Azure OpenAI client with token provider and custom HTTP client
            self.client = AzureOpenAI(
                api_version=self.api_version,
                azure_endpoint=self.api_endpoint,
                azure_ad_token_provider=token_provider,
                http_client=http_client
            )
            
            self._initialized = True
            logger.info(f"VectorEmbeddingsHelper initialized successfully with deployment: {self.embedding_deployment}")
            
        except Exception as e:
            logger.error(f"Error initializing VectorEmbeddingsHelper: {str(e)}", exc_info=True)
            raise
    
    async def get_embeddings(self, text: str) -> List[float]:
        """Generate vector embeddings for the given text."""
        try:
            logger.info(f"Generating embeddings for text (length: {len(text)})")
            
            # Truncate text if it's too long (OpenAI has a token limit)
            max_length = 8192  # Maximum length for text-embedding-3-large
            if len(text) > max_length:
                logger.warning(f"Text too long ({len(text)} chars), truncating to {max_length} chars")
                text = text[:max_length]
            
            # Generate embeddings
            response = self.client.embeddings.create(
                input=text,
                model=self.embedding_deployment
            )
            
            # Extract the embedding vector
            embedding = response.data[0].embedding
            logger.info(f"Successfully generated embeddings (dimensions: {len(embedding)})")
            
            return embedding
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}", exc_info=True)
            raise

# Create a singleton instance
vector_embeddings_helper = None

def get_vector_embeddings_helper() -> VectorEmbeddingsHelper:
    """Get or create the VectorEmbeddingsHelper singleton."""
    global vector_embeddings_helper
    if vector_embeddings_helper is None:
        vector_embeddings_helper = VectorEmbeddingsHelper()
    return vector_embeddings_helper
