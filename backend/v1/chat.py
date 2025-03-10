from fastapi import APIRouter, HTTPException, Body
from typing import List, Optional, Tuple
from pydantic import BaseModel
import os
import logging
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from openai import AzureOpenAI
import httpx

from backend.utils.cosmos_db import get_cosmos_db_client
from backend.utils.cosmos_db_extensions import get_cosmos_db_extensions
from backend.utils.vector_embeddings import get_vector_embeddings_helper
from backend.utils.logger import get_logger
from backend.v1.models import SearchResponse

# Set up logger
logger = get_logger(__name__)

router = APIRouter()

# Chat models
class Citation(BaseModel):
    source_id: str
    source_name: str
    page_id: str
    page_title: Optional[str] = None
    text_snippet: str
    similarity: float

class ChatMessage(BaseModel):
    role: str
    content: str
    citations: Optional[List[Citation]] = None

class ChatRequest(BaseModel):
    message: str
    vector_search: bool = True
    sources_limit: int = 5
    source_ids: Optional[List[str]] = None

class ChatResponse(BaseModel):
    data: ChatMessage
    success: bool = True
    message: Optional[str] = None

class ChatHelper:
    """Helper class for chat functionality using Azure OpenAI API."""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one instance of the helper is created."""
        if cls._instance is None:
            cls._instance = super(ChatHelper, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the Azure OpenAI client."""
        if self._initialized:
            return
            
        logger.info("Initializing ChatHelper")
        
        # Get environment variables
        self.api_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        self.api_version = os.environ.get("AZURE_OPENAI_API_VERSION", "2024-06-01")
        self.chat_deployment = os.environ.get("AOAI_CHAT_DEPLOYMENT", "gpt-4o")
        
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
            logger.info(f"ChatHelper initialized successfully with deployment: {self.chat_deployment}")
            
        except Exception as e:
            logger.error(f"Error initializing ChatHelper: {str(e)}", exc_info=True)
            raise
    
    async def get_relevant_context(self, query: str, limit: int = 5, source_ids: Optional[List[str]] = None) -> Tuple[str, List[Citation]]:
        """Get relevant context from the archive based on the query.
        
        Args:
            query (str): The user's query
            limit (int, optional): Maximum number of results to return. Defaults to 5.
            source_ids (Optional[List[str]], optional): List of source IDs to filter by. Defaults to None.
            
        Returns:
            Tuple[str, List[Citation]]: A tuple containing the context string and a list of citations
        """
        try:
            # Generate vector embeddings for the query
            vector_embeddings = get_vector_embeddings_helper()
            query_vector = await vector_embeddings.get_embeddings(query)
            
            # Use vector search to find similar pages
            cosmos_extensions = get_cosmos_db_extensions()
            
            # Construct a query that uses the VectorDistance function
            vector_query = f"""
            SELECT TOP {limit} c.id, c.sourceId, c.imageUrl, c.extractedText, c.title, c.date, c.notes, c.createdAt, c.updatedAt,
                   VectorDistance(c.contentVector, @queryVector) AS similarity
            FROM c
            WHERE c.contentVector != null AND ARRAY_LENGTH(c.contentVector) > 0
            """
            
            # Add source filter if source_ids is provided
            if source_ids and len(source_ids) > 0:
                source_ids_str = ", ".join([f"'{s}'" for s in source_ids])
                vector_query += f" AND c.sourceId IN ({source_ids_str})"
                
            vector_query += " ORDER BY VectorDistance(c.contentVector, @queryVector)"
            
            # Execute the query
            vector_params = [{"name": "@queryVector", "value": query_vector}]
            vector_results = await cosmos_extensions.query_pages(vector_query, vector_params)
            
            # Get the sources for these pages
            cosmos_client = get_cosmos_db_client()
            context_parts = []
            citations = []
            
            for page in vector_results:
                source_id = page["sourceId"]
                page_id = page["id"]
                similarity = page["similarity"]
                source = await cosmos_client.get_source(source_id)
                
                if source:
                    source_name = source.get("name", "Unknown Source")
                    page_title = page.get("title", "Untitled Page")
                    page_text = page.get("extractedText", "")
                    
                    # Add this page's content to the context
                    context_part = f"Source: {source_name}\nPage: {page_title}\nContent: {page_text}\n\n"
                    context_parts.append(context_part)
                    
                    # Create a citation
                    # Extract a snippet (first 150 chars) for the citation
                    text_snippet = page_text[:150] + "..." if len(page_text) > 150 else page_text
                    
                    citation = Citation(
                        source_id=source_id,
                        source_name=source_name,
                        page_id=page_id,
                        page_title=page_title if page_title else None,
                        text_snippet=text_snippet,
                        similarity=similarity
                    )
                    citations.append(citation)
            
            # Combine all context parts
            context = "".join(context_parts)
            
            # Truncate if too long (OpenAI has a token limit)
            max_length = 14000  # Conservative limit for gpt-4o
            if len(context) > max_length:
                logger.warning(f"Context too long ({len(context)} chars), truncating to {max_length} chars")
                context = context[:max_length]
            
            return context, citations
        
        except Exception as e:
            logger.error(f"Error getting relevant context: {str(e)}", exc_info=True)
            return "", []
    
    async def generate_response(self, user_message: str, context: str = "") -> str:
        """Generate a response to the user's message using the chat model."""
        try:
            logger.info(f"Generating response for message (length: {len(user_message)})")
            
            # Prepare the system message with context
            system_message = """You are an AI assistant for a personal archive system. 
You help users find and understand information from their personal archives, such as journals, notes, and documents.
Respond in a helpful, concise, and accurate manner based on the information in the archive.
If you don't know the answer or can't find relevant information in the archive, be honest about it.
"""
            
            if context:
                system_message += "\n\nHere is relevant information from the archive that may help answer the user's question:\n\n" + context
            
            # Generate response
            response = self.client.chat.completions.create(
                model=self.chat_deployment,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Extract the response text
            response_text = response.choices[0].message.content
            logger.info(f"Successfully generated response (length: {len(response_text)})")
            
            return response_text
        
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}", exc_info=True)
            raise

# Create a singleton instance
chat_helper = None

def get_chat_helper() -> ChatHelper:
    """Get or create the ChatHelper singleton."""
    global chat_helper
    if chat_helper is None:
        chat_helper = ChatHelper()
    return chat_helper

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest = Body(...)):
    """
    Generate a chat response based on the user's message.
    
    Args:
        request (ChatRequest): The chat request containing the user's message.
    
    Returns:
        ChatResponse: The chat response.
    """
    try:
        logger.info(f"Chat request received: {request.message[:50]}...")
        
        # Get the chat helper
        helper = get_chat_helper()
        
        # Get relevant context and citations if vector search is enabled
        context = ""
        citations = []
        if request.vector_search:
            context, citations = await helper.get_relevant_context(
                request.message, 
                request.sources_limit,
                request.source_ids
            )
            source_info = f", sources: {len(request.source_ids) if request.source_ids else 'all'}"
            logger.info(f"Retrieved context for RAG (length: {len(context)}, citations: {len(citations)}, limit: {request.sources_limit}{source_info})")
        
        # Generate response
        response_text = await helper.generate_response(request.message, context)
        
        # Return the response with citations
        return ChatResponse(
            data=ChatMessage(
                role="assistant", 
                content=response_text,
                citations=citations if citations else None
            )
        )
    
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating chat response: {str(e)}")
