from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from backend.utils.cosmos_db import get_cosmos_db_client
from backend.utils.cosmos_db_extensions import get_cosmos_db_extensions
from backend.utils.vector_embeddings import get_vector_embeddings_helper
from backend.utils.logger import get_logger
from backend.v1.models import SearchResponse

# Set up logger
logger = get_logger(__name__)

router = APIRouter()

@router.get("/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., description="Search query"),
    limit: int = Query(10, description="Maximum number of results to return"),
    vector: bool = Query(False, description="Whether to use vector search"),
    source_ids: Optional[str] = Query(None, description="Comma-separated list of source IDs to filter by")
):
    """
    Search for content across sources and pages.
    
    Args:
        q (str): Search query.
        limit (int, optional): Maximum number of results to return. Defaults to 10.
        vector (bool, optional): Whether to use vector search. Defaults to False.
        source_ids (str, optional): Comma-separated list of source IDs to filter by. If not provided, all sources are searched.
    
    Returns:
        SearchResponse: Search results.
    """
    try:
        # Parse source_ids if provided
        source_id_list = []
        if source_ids:
            source_id_list = [s.strip() for s in source_ids.split(",") if s.strip()]
            logger.info(f"Searching for: {q} (vector={vector}, limit={limit}, sources={len(source_id_list)})")
        else:
            logger.info(f"Searching for: {q} (vector={vector}, limit={limit}, sources=all)")
        cosmos_client = get_cosmos_db_client()
        cosmos_extensions = get_cosmos_db_extensions()
        
        # Initialize results
        sources = []
        pages = []
        
        if vector:
            # Generate vector embeddings for the search query
            vector_embeddings = get_vector_embeddings_helper()
            query_vector = await vector_embeddings.get_embeddings(q)
            
            # Use vector search to find similar pages
            # Construct a query that uses the VectorDistance function
            vector_query = f"""
            SELECT TOP {limit} c.id, c.sourceId, c.imageUrl, c.extractedText, c.title, c.date, c.notes, c.createdAt, c.updatedAt,
                   VectorDistance(c.contentVector, @queryVector) AS similarity
            FROM c
            WHERE c.contentVector != null AND ARRAY_LENGTH(c.contentVector) > 0
            """
            
            # Add source filter if source_ids is provided
            if source_id_list:
                source_ids_str = ", ".join([f"'{s}'" for s in source_id_list])
                vector_query += f" AND c.sourceId IN ({source_ids_str})"
                
            vector_query += " ORDER BY VectorDistance(c.contentVector, @queryVector)"
            
            # Execute the query
            vector_params = [{"name": "@queryVector", "value": query_vector}]
            vector_results = await cosmos_extensions.query_pages(vector_query, vector_params)
            
            # Convert to Page models
            for page in vector_results:
                # Get the source for this page
                source_id = page["sourceId"]
                source = await cosmos_client.get_source(source_id)
                
                if source:
                    # Add the source to the results if it's not already there
                    if not any(s["id"] == source_id for s in sources):
                        sources.append({
                            "id": source["id"],
                            "name": source["name"],
                            "description": source.get("description"),
                            "userId": source["userId"],
                            "createdAt": source["createdAt"],
                            "updatedAt": source["updatedAt"]
                        })
                    
                    # Add the page to the results
                    pages.append({
                        "id": page["id"],
                        "sourceId": page["sourceId"],
                        "imageUrl": page["imageUrl"],
                        "extractedText": page.get("extractedText", ""),
                        "title": page.get("title"),
                        "date": page.get("date"),
                        "notes": page.get("notes"),
                        "createdAt": page["createdAt"],
                        "updatedAt": page["updatedAt"],
                        "similarity": page["similarity"]
                    })
        else:
            # Use full-text search to find sources and pages
            # Search for sources (case-insensitive)
            source_query = f"""
            SELECT TOP {limit} *
            FROM c
            WHERE CONTAINS(LOWER(c.name), LOWER(@query)) OR CONTAINS(LOWER(c.description), LOWER(@query))
            """
            
            source_params = [{"name": "@query", "value": q}]
            source_results = await cosmos_extensions.query_sources(source_query, source_params)
            
            # Convert to Source models
            sources = [
                {
                    "id": source["id"],
                    "name": source["name"],
                    "description": source.get("description"),
                    "userId": source["userId"],
                    "createdAt": source["createdAt"],
                    "updatedAt": source["updatedAt"]
                }
                for source in source_results
            ]
            
            # Search for pages (case-insensitive)
            page_query = f"""
            SELECT TOP {limit} *
            FROM c
            WHERE (CONTAINS(LOWER(c.extractedText), LOWER(@query)) OR CONTAINS(LOWER(c.notes), LOWER(@query)) OR CONTAINS(LOWER(c.title), LOWER(@query)))
            """
            
            # Add source filter if source_ids is provided
            if source_id_list:
                source_ids_str = ", ".join([f"'{s}'" for s in source_id_list])
                page_query += f" AND c.sourceId IN ({source_ids_str})"
            
            page_params = [{"name": "@query", "value": q}]
            page_results = await cosmos_extensions.query_pages(page_query, page_params)
            
            # Convert to Page models
            pages = [
                {
                    "id": page["id"],
                    "sourceId": page["sourceId"],
                    "imageUrl": page["imageUrl"],
                    "extractedText": page.get("extractedText", ""),
                    "title": page.get("title"),
                    "date": page.get("date"),
                    "notes": page.get("notes"),
                    "createdAt": page["createdAt"],
                    "updatedAt": page["updatedAt"]
                }
                for page in page_results
            ]
        
        # Return the search results
        return SearchResponse(data={"sources": sources, "pages": pages})
    
    except Exception as e:
        logger.error(f"Error searching: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error searching: {str(e)}")
