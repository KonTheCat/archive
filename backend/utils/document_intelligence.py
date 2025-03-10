import os
import logging
from typing import Optional
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential

from backend.utils.logger import get_logger

# Set up logger
logger = get_logger(__name__)

class DocumentIntelligenceHelper:
    """Helper for interacting with Azure Document Intelligence."""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one instance of the helper is created."""
        if cls._instance is None:
            cls._instance = super(DocumentIntelligenceHelper, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the Document Intelligence helper using environment variables."""
        if self._initialized:
            return
            
        logger.info("Initializing DocumentIntelligenceHelper")
        
        # Get environment variables
        self.endpoint = os.environ.get("DOCUMENT_INTELLIGENCE_ENDPOINT")
        self.key = os.environ.get("DOCUMENT_INTELLIGENCE_KEY")
        
        # Validate environment variables
        if not self.endpoint:
            logger.error("Missing required environment variable: DOCUMENT_INTELLIGENCE_ENDPOINT")
            raise ValueError("DOCUMENT_INTELLIGENCE_ENDPOINT environment variable must be set")
        
        try:
            # Create the client
            logger.info("Creating DocumentIntelligenceClient")
            
            # Use key if available, otherwise use DefaultAzureCredential
            if self.key:
                logger.info("Using API key authentication")
                self.client = DocumentIntelligenceClient(
                    endpoint=self.endpoint,
                    credential=AzureKeyCredential(self.key)
                )
            else:
                logger.info("Using DefaultAzureCredential")
                self.client = DocumentIntelligenceClient(
                    endpoint=self.endpoint,
                    credential=DefaultAzureCredential()
                )
            
            self._initialized = True
            logger.info("DocumentIntelligenceHelper initialization completed successfully")
            
        except Exception as e:
            logger.error(f"Error initializing DocumentIntelligenceHelper: {str(e)}", exc_info=True)
            raise
    
    async def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from an image using Azure Document Intelligence.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted text as a string
        """
        logger.info(f"Extracting text from image: {image_path}")
        
        try:
            # Open the image file
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            # Analyze the document
            logger.info("Calling Document Intelligence API")
            poller = self.client.begin_analyze_document(
                "prebuilt-read",
                body=image_data
            )
            
            # Get the result
            result = poller.result()
            
            # Extract the text
            extracted_text = ""
            for page in result.pages:
                for line in page.lines:
                    extracted_text += line.content + "\n"
            
            logger.info(f"Text extraction completed. Extracted {len(extracted_text)} characters")
            return extracted_text
            
        except Exception as e:
            logger.error(f"Error extracting text from image: {str(e)}", exc_info=True)
            raise

# Create a singleton instance
document_intelligence_helper = None

def get_document_intelligence_helper() -> DocumentIntelligenceHelper:
    """Get or create the DocumentIntelligenceHelper singleton."""
    global document_intelligence_helper
    if document_intelligence_helper is None:
        document_intelligence_helper = DocumentIntelligenceHelper()
    return document_intelligence_helper
