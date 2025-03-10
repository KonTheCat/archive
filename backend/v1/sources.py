import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from backend.utils.cosmos_db import get_cosmos_db_client
from backend.utils.logger import get_logger
from backend.v1.models import Source, SourceCreate, SourceResponse, SourcesResponse

# Set up logger
logger = get_logger(__name__)

router = APIRouter()

@router.get("/sources", response_model=SourcesResponse)
async def get_sources():
    """Get all sources."""
    try:
        logger.info("Getting all sources")
        cosmos_client = get_cosmos_db_client()
        
        # Use the sources container
        sources = await cosmos_client.get_sources()
        
        # Convert to Source model
        source_models = [
            Source(
                id=source["id"],
                name=source["name"],
                description=source.get("description"),
                userId=source["userId"],
                startDate=source.get("startDate"),
                endDate=source.get("endDate"),
                createdAt=source["createdAt"],
                updatedAt=source["updatedAt"]
            )
            for source in sources
        ]
        
        return SourcesResponse(data=source_models)
    except Exception as e:
        logger.error(f"Error getting sources: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting sources: {str(e)}")

@router.get("/sources/{source_id}", response_model=SourceResponse)
async def get_source(source_id: str):
    """Get a source by ID."""
    try:
        logger.info(f"Getting source with ID: {source_id}")
        cosmos_client = get_cosmos_db_client()
        
        # Use the sources container
        source = await cosmos_client.get_source(source_id)
        
        if not source:
            raise HTTPException(status_code=404, detail=f"Source with ID {source_id} not found")
        
        # Convert to Source model
        source_model = Source(
            id=source["id"],
            name=source["name"],
            description=source.get("description"),
            userId=source["userId"],
            startDate=source.get("startDate"),
            endDate=source.get("endDate"),
            createdAt=source["createdAt"],
            updatedAt=source["updatedAt"]
        )
        
        return SourceResponse(data=source_model)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting source: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting source: {str(e)}")

@router.post("/sources", response_model=SourceResponse)
async def create_source(source: SourceCreate):
    """Create a new source."""
    try:
        logger.info(f"Creating new source: {source.name}")
        cosmos_client = get_cosmos_db_client()
        
        # Generate a new ID
        source_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        # Create the source document
        source_doc = {
            "id": source_id,
            "name": source.name,
            "description": source.description,
            "userId": source.userId,
            "startDate": source.startDate,
            "endDate": source.endDate,
            "createdAt": now,
            "updatedAt": now
        }
        
        # Use the sources container
        created_source = await cosmos_client.create_source(source_doc)
        
        # Convert to Source model
        source_model = Source(
            id=created_source["id"],
            name=created_source["name"],
            description=created_source.get("description"),
            userId=created_source["userId"],
            startDate=created_source.get("startDate"),
            endDate=created_source.get("endDate"),
            createdAt=created_source["createdAt"],
            updatedAt=created_source["updatedAt"]
        )
        
        return SourceResponse(data=source_model)
    except Exception as e:
        logger.error(f"Error creating source: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error creating source: {str(e)}")

@router.put("/sources/{source_id}", response_model=SourceResponse)
async def update_source(source_id: str, source_update: dict):
    """Update an existing source."""
    try:
        logger.info(f"Updating source with ID: {source_id}")
        cosmos_client = get_cosmos_db_client()
        
        # Get the current source
        existing_source = await cosmos_client.get_source(source_id)
        if not existing_source:
            raise HTTPException(status_code=404, detail=f"Source with ID {source_id} not found")
        
        # Update the source with the new values
        now = datetime.now().isoformat()
        updates = {
            "updatedAt": now
        }
        
        # Only update fields that are provided
        if "name" in source_update:
            updates["name"] = source_update["name"]
        if "description" in source_update:
            updates["description"] = source_update["description"]
        if "startDate" in source_update:
            updates["startDate"] = source_update["startDate"]
        if "endDate" in source_update:
            updates["endDate"] = source_update["endDate"]
        
        # Update the source in the database
        updated_source = await cosmos_client.update_source(source_id, updates)
        
        # Convert to Source model
        source_model = Source(
            id=updated_source["id"],
            name=updated_source["name"],
            description=updated_source.get("description"),
            userId=updated_source["userId"],
            startDate=updated_source.get("startDate"),
            endDate=updated_source.get("endDate"),
            createdAt=updated_source["createdAt"],
            updatedAt=updated_source["updatedAt"]
        )
        
        return SourceResponse(data=source_model)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating source: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error updating source: {str(e)}")
