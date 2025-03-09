import os
import logging
import datetime
from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult

# Set up logger
logger = logging.getLogger(__name__)

class DocumentIntelligenceHelper:
    """
    Helper class for Azure Document Intelligence operations.
    Uses the most basic document model (prebuilt-layout) for text extraction.
    """
    
    def __init__(self):
        """
        Initialize the Document Intelligence client using DefaultAzureCredential.
        """
        # Get the Document Intelligence resource name from environment variables
        self.resource_name = os.environ.get("DOCUMENT_INTELLIGENCE_NAME")
        if not self.resource_name:
            raise ValueError("DOCUMENT_INTELLIGENCE_NAME environment variable is not set")
        
        # Construct the endpoint URL
        self.endpoint = f"https://{self.resource_name}.cognitiveservices.azure.com/"
        
        # Use DefaultAzureCredential for authentication
        self.credential = DefaultAzureCredential()
        
        # Create the Document Intelligence client
        self.client = DocumentIntelligenceClient(
            endpoint=self.endpoint,
            credential=self.credential
        )
        
        logger.info(f"Document Intelligence client initialized with endpoint: {self.endpoint}")
    
    async def extract_text_from_image(self, image_path, is_url=False):
        """
        Extract text from an image using Azure Document Intelligence.
        
        Args:
            image_path (str): Path to the image file or URL of the image.
            is_url (bool): Whether the image_path is a URL or a local file path.
            
        Returns:
            str: Extracted text from the image.
        """
        try:
            logger.info(f"Extracting text from {'URL' if is_url else 'file'}: {image_path}")
            
            if is_url:
                # Analyze document from URL
                from azure.ai.documentintelligence.models import AnalyzeDocumentRequest
                poller = self.client.begin_analyze_document(
                    "prebuilt-layout",  # Using the most basic document model
                    AnalyzeDocumentRequest(url_source=image_path)
                )
            else:
                # Analyze document from file
                with open(image_path, "rb") as f:
                    poller = self.client.begin_analyze_document(
                        "prebuilt-layout",  # Using the most basic document model
                        body=f
                    )
            
            # Wait for the operation to complete
            result: AnalyzeResult = poller.result()
            
            # Extract text from the result
            extracted_text = ""
            
            # Extract text from paragraphs if available
            if result.paragraphs:
                # Sort paragraphs by their position in the document
                result.paragraphs.sort(key=lambda p: (
                    p.bounding_regions[0].page_number if p.bounding_regions else 0,
                    p.spans[0].offset if p.spans else 0
                ))
                
                # Concatenate paragraph content
                extracted_text = "\n\n".join([p.content for p in result.paragraphs])
            
            # If no paragraphs, try to extract from pages
            elif result.pages:
                for page in result.pages:
                    if page.lines:
                        page_text = "\n".join([line.content for line in page.lines])
                        extracted_text += page_text + "\n\n"
            
            logger.info(f"Successfully extracted text from {'URL' if is_url else 'file'}: {image_path}")
            return extracted_text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from {'URL' if is_url else 'file'} {image_path}: {str(e)}", exc_info=True)
            return f"Error extracting text: {str(e)}"

# Singleton instance
_document_intelligence_helper = None

def get_document_intelligence_helper():
    """
    Get a singleton instance of the DocumentIntelligenceHelper.
    
    Returns:
        DocumentIntelligenceHelper: A singleton instance of the DocumentIntelligenceHelper.
    """
    global _document_intelligence_helper
    if _document_intelligence_helper is None:
        _document_intelligence_helper = DocumentIntelligenceHelper()
    return _document_intelligence_helper
