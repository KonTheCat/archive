import uuid
import os
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, BackgroundTasks
from azure.storage.blob import BlobServiceClient, BlobSasPermissions, generate_blob_sas

from backend.utils.cosmos_db import get_cosmos_db_client
from backend.utils.blob_storage import get_blob_storage_client
from backend.utils.logger import get_logger
from backend.v1.text_extraction import schedule_text_extraction
from backend.v1.models import Page, PageResponse, PagesResponse

# Set up logger
logger = get_logger(__name__)

router = APIRouter()

@router.get("/sources/{source_id}/pages", response_model=PagesResponse)
async def get_pages(source_id: str):
    """Get all pages for a source."""
    try:
        logger.info(f"Getting pages for source ID: {source_id}")
        cosmos_client = get_cosmos_db_client()
        
        # Check if source exists
        source = await cosmos_client.get_source(source_id)
        if not source:
            raise HTTPException(status_code=404, detail=f"Source with ID {source_id} not found")
        
        # Use the pages container
        pages = await cosmos_client.get_pages(source_id)
        
        # Convert to Page model
        page_models = [
            Page(
                id=page["id"],
                sourceId=page["sourceId"],
                imageUrl=page["imageUrl"],
                extractedText=page.get("extractedText", ""),
                title=page.get("title"),
                date=page.get("date"),
                notes=page.get("notes"),
                createdAt=page["createdAt"],
                updatedAt=page["updatedAt"]
            )
            for page in pages
        ]
        
        return PagesResponse(data=page_models)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting pages: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting pages: {str(e)}")

@router.get("/sources/{source_id}/pages/{page_id}", response_model=PageResponse)
async def get_page(source_id: str, page_id: str):
    """Get a page by ID with a user-delegated SAS token for the image URL."""
    try:
        logger.info(f"Getting page with ID: {page_id} from source ID: {source_id}")
        cosmos_client = get_cosmos_db_client()
        blob_client = get_blob_storage_client()
        
        # Check if source exists
        source = await cosmos_client.get_source(source_id)
        if not source:
            raise HTTPException(status_code=404, detail=f"Source with ID {source_id} not found")
        
        # Get the page document
        page = await cosmos_client.get_page(source_id, page_id)
        if not page:
            raise HTTPException(status_code=404, detail=f"Page with ID {page_id} not found")
        
        # Get the storage account name from environment
        storage_account_name = os.environ.get("STORAGE_ACCOUNT_NAME")
        if not storage_account_name:
            raise HTTPException(status_code=500, detail="Storage account name not configured")
        
        # Parse the blob URL to get container and blob name
        original_url = page["imageUrl"]
        url_parts = original_url.replace(f"https://{storage_account_name}.blob.core.windows.net/", "").split("/")
        container_name = url_parts[0]
        blob_name = "/".join(url_parts[1:])
        
        # Create a BlobServiceClient
        account_url = f"https://{storage_account_name}.blob.core.windows.net"
        blob_service_client = BlobServiceClient(account_url=account_url, credential=blob_client.credential)
        
        # Get a user delegation key
        delegation_key_start_time = datetime.now(timezone.utc) - timedelta(minutes=5)
        delegation_key_expiry_time = datetime.now(timezone.utc) + timedelta(minutes=30)
        
        user_delegation_key = blob_service_client.get_user_delegation_key(
            key_start_time=delegation_key_start_time,
            key_expiry_time=delegation_key_expiry_time
        )
        
        # Get a blob client for the specific blob
        blob_client_instance = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        
        # Generate SAS token
        sas_token = generate_blob_sas(
            account_name=blob_client_instance.account_name,
            container_name=blob_client_instance.container_name,
            blob_name=blob_client_instance.blob_name,
            user_delegation_key=user_delegation_key,
            permission=BlobSasPermissions(read=True),
            expiry=delegation_key_expiry_time,
            start=delegation_key_start_time
        )
        
        # Create the full URL with SAS token
        sas_url = f"{blob_client_instance.url}?{sas_token}"
        
        # Create the Page model with the SAS URL
        page_model = Page(
            id=page["id"],
            sourceId=page["sourceId"],
            imageUrl=sas_url,  # Use the SAS URL instead of the direct URL
            extractedText=page.get("extractedText", ""),
            title=page.get("title"),
            date=page.get("date"),
            notes=page.get("notes"),
            createdAt=page["createdAt"],
            updatedAt=page["updatedAt"]
        )
        
        return PageResponse(data=page_model)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting page: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting page: {str(e)}")

@router.post("/sources/{source_id}/pages", response_model=PageResponse)
async def create_page(
    source_id: str,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    date: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Create a new page with an image file."""
    try:
        logger.info(f"Creating new page for source ID: {source_id}")
        cosmos_client = get_cosmos_db_client()
        blob_client = get_blob_storage_client()
        
        # Check if source exists
        source = await cosmos_client.get_source(source_id)
        if not source:
            raise HTTPException(status_code=404, detail=f"Source with ID {source_id} not found")
        
        # Upload the file to blob storage
        content_type = file.content_type or "application/octet-stream"
        
        # Determine the path in blob storage: Source/Page
        file_name = f"{source_id}/{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
        
        # Upload the file
        upload_result = await blob_client.upload_file(file.file, file_name, content_type)
        
        # Generate a new ID for the page
        page_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        # Initial placeholder for extracted text
        extracted_text = "Text extraction in progress..."
        
        # Create the page document
        page_doc = {
            "id": page_id,
            "sourceId": source_id,  # Use sourceId to match the Cosmos DB schema
            "imageUrl": upload_result["url"],
            "extractedText": extracted_text,
            "title": title,
            "date": date,
            "notes": notes,
            "createdAt": now,
            "updatedAt": now
        }
        
        # Use the pages container
        created_page = await cosmos_client.create_page(page_doc)
        
        # Schedule text extraction as a background task
        # Get a SAS URL for the blob to use in the background task
        storage_account_name = os.environ.get("STORAGE_ACCOUNT_NAME")
        if storage_account_name:
                # Parse the blob URL to get container and blob name
                original_url = upload_result["url"]
                url_parts = original_url.replace(f"https://{storage_account_name}.blob.core.windows.net/", "").split("/")
                container_name = url_parts[0]
                blob_name = "/".join(url_parts[1:])
                
                # Create a BlobServiceClient
                account_url = f"https://{storage_account_name}.blob.core.windows.net"
                blob_service_client = BlobServiceClient(account_url=account_url, credential=blob_client.credential)
                
                # Get a user delegation key
                delegation_key_start_time = datetime.now(timezone.utc) - timedelta(minutes=5)
                delegation_key_expiry_time = datetime.now(timezone.utc) + timedelta(minutes=30)
                
                user_delegation_key = blob_service_client.get_user_delegation_key(
                    key_start_time=delegation_key_start_time,
                    key_expiry_time=delegation_key_expiry_time
                )
                
                # Get a blob client for the specific blob
                blob_client_instance = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
                
                # Generate SAS token
                sas_token = generate_blob_sas(
                    account_name=blob_client_instance.account_name,
                    container_name=blob_client_instance.container_name,
                    blob_name=blob_client_instance.blob_name,
                    user_delegation_key=user_delegation_key,
                    permission=BlobSasPermissions(read=True),
                    expiry=delegation_key_expiry_time,
                    start=delegation_key_start_time
                )
                
                # Create the full URL with SAS token
                sas_url = f"{blob_client_instance.url}?{sas_token}"
                
                # Ensure the page exists in Cosmos DB before scheduling text extraction
                page_check = await cosmos_client.get_page(source_id, page_id)
                if page_check:
                    # Schedule the text extraction task
                    schedule_text_extraction(background_tasks, sas_url, source_id, page_id)
                    logger.info(f"Scheduled text extraction for page {page_id} in source {source_id}")
                else:
                    logger.error(f"Page {page_id} not found in Cosmos DB after creation. Text extraction not scheduled.")
        
        # Convert to Page model
        page_model = Page(
            id=created_page["id"],
            sourceId=created_page["sourceId"],
            imageUrl=created_page["imageUrl"],
            extractedText=created_page["extractedText"],
            title=created_page.get("title"),
            date=created_page.get("date"),
            notes=created_page.get("notes"),
            createdAt=created_page["createdAt"],
            updatedAt=created_page["updatedAt"]
        )
        
        return PageResponse(data=page_model)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating page: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error creating page: {str(e)}")

@router.put("/sources/{source_id}/pages/{page_id}", response_model=PageResponse)
async def update_page(source_id: str, page_id: str, page_update: dict):
    """Update a page by ID."""
    try:
        logger.info(f"Updating page with ID: {page_id} from source ID: {source_id}")
        cosmos_client = get_cosmos_db_client()
        
        # Check if source exists
        source = await cosmos_client.get_source(source_id)
        if not source:
            raise HTTPException(status_code=404, detail=f"Source with ID {source_id} not found")
        
        # Get the page document
        page = await cosmos_client.get_page(source_id, page_id)
        if not page:
            raise HTTPException(status_code=404, detail=f"Page with ID {page_id} not found")
        
        # Update only the fields that are provided
        update_data = {k: v for k, v in page_update.items() if v is not None}
        update_data["updatedAt"] = datetime.now().isoformat()
        
        # Update the page document
        updated_page = await cosmos_client.update_page(source_id, page_id, update_data)
        
        # Convert to Page model
        page_model = Page(
            id=updated_page["id"],
            sourceId=updated_page["sourceId"],
            imageUrl=updated_page["imageUrl"],
            extractedText=updated_page.get("extractedText", ""),
            title=updated_page.get("title"),
            date=updated_page.get("date"),
            notes=updated_page.get("notes"),
            createdAt=updated_page["createdAt"],
            updatedAt=updated_page["updatedAt"]
        )
        
        return PageResponse(data=page_model)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating page: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error updating page: {str(e)}")

@router.delete("/sources/{source_id}/pages/{page_id}")
async def delete_page(source_id: str, page_id: str):
    """Delete a page by ID."""
    try:
        logger.info(f"Deleting page with ID: {page_id} from source ID: {source_id}")
        cosmos_client = get_cosmos_db_client()
        blob_client = get_blob_storage_client()
        
        # Check if source exists
        source = await cosmos_client.get_source(source_id)
        if not source:
            raise HTTPException(status_code=404, detail=f"Source with ID {source_id} not found")
        
        # Get the page document
        page = await cosmos_client.get_page(source_id, page_id)
        if not page:
            raise HTTPException(status_code=404, detail=f"Page with ID {page_id} not found")
        
        # Get the storage account name from environment
        storage_account_name = os.environ.get("STORAGE_ACCOUNT_NAME")
        if not storage_account_name:
            raise HTTPException(status_code=500, detail="Storage account name not configured")
        
        # Parse the blob URL to get container and blob name
        original_url = page["imageUrl"]
        url_parts = original_url.replace(f"https://{storage_account_name}.blob.core.windows.net/", "").split("/")
        container_name = url_parts[0]
        blob_name = "/".join(url_parts[1:])
        
        # Delete the blob from storage
        await blob_client.delete_file(blob_name)
        
        # Delete the page document from Cosmos DB
        await cosmos_client.delete_page(source_id, page_id)
        
        return {"success": True, "message": "Page deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting page: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error deleting page: {str(e)}")

@router.post("/sources/{source_id}/pages/upload", response_model=PagesResponse)
async def upload_multiple_pages(
    source_id: str,
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Upload multiple pages at once."""
    try:
        logger.info(f"Uploading multiple pages for source ID: {source_id}")
        cosmos_client = get_cosmos_db_client()
        blob_client = get_blob_storage_client()
        
        # Check if source exists
        source = await cosmos_client.get_source(source_id)
        if not source:
            raise HTTPException(status_code=404, detail=f"Source with ID {source_id} not found")
        
        created_pages = []
        
        for file in files:
            # Upload the file to blob storage
            content_type = file.content_type or "application/octet-stream"
            
            # Determine the path in blob storage: Source/Page
            file_name = f"{source_id}/{uuid.uuid4()}{os.path.splitext(file.filename)[1]}"
            
            # Upload the file
            upload_result = await blob_client.upload_file(file.file, file_name, content_type)
            
            # Generate a new ID for the page
            page_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            
            # Initial placeholder for extracted text
            extracted_text = "Text extraction in progress..."
            
            # Create the page document
            page_doc = {
                "id": page_id,
                "sourceId": source_id,  # Use sourceId to match the Cosmos DB schema
                "imageUrl": upload_result["url"],
                "extractedText": extracted_text,
                "title": os.path.splitext(file.filename)[0],  # Use filename as default title
                "createdAt": now,
                "updatedAt": now
            }
            
            # Use the pages container
            created_page = await cosmos_client.create_page(page_doc)
            
            # Schedule text extraction as a background task
            # Get a SAS URL for the blob to use in the background task
            storage_account_name = os.environ.get("STORAGE_ACCOUNT_NAME")
            if storage_account_name:
                    # Parse the blob URL to get container and blob name
                    original_url = upload_result["url"]
                    url_parts = original_url.replace(f"https://{storage_account_name}.blob.core.windows.net/", "").split("/")
                    container_name = url_parts[0]
                    blob_name = "/".join(url_parts[1:])
                    
                    # Create a BlobServiceClient
                    account_url = f"https://{storage_account_name}.blob.core.windows.net"
                    blob_service_client = BlobServiceClient(account_url=account_url, credential=blob_client.credential)
                    
                    # Get a user delegation key
                    delegation_key_start_time = datetime.now(timezone.utc) - timedelta(minutes=5)
                    delegation_key_expiry_time = datetime.now(timezone.utc) + timedelta(minutes=30)
                    
                    user_delegation_key = blob_service_client.get_user_delegation_key(
                        key_start_time=delegation_key_start_time,
                        key_expiry_time=delegation_key_expiry_time
                    )
                    
                    # Get a blob client for the specific blob
                    blob_client_instance = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
                    
                    # Generate SAS token
                    sas_token = generate_blob_sas(
                        account_name=blob_client_instance.account_name,
                        container_name=blob_client_instance.container_name,
                        blob_name=blob_client_instance.blob_name,
                        user_delegation_key=user_delegation_key,
                        permission=BlobSasPermissions(read=True),
                        expiry=delegation_key_expiry_time,
                        start=delegation_key_start_time
                    )
                    
                    # Create the full URL with SAS token
                    sas_url = f"{blob_client_instance.url}?{sas_token}"
                    
                    # Ensure the page exists in Cosmos DB before scheduling text extraction
                    page_check = await cosmos_client.get_page(source_id, page_id)
                    if page_check:
                        # Schedule the text extraction task
                        schedule_text_extraction(background_tasks, sas_url, source_id, page_id)
                        logger.info(f"Scheduled text extraction for page {page_id} in source {source_id}")
                    else:
                        logger.error(f"Page {page_id} not found in Cosmos DB after creation. Text extraction not scheduled.")
            
            # Convert to Page model
            page_model = Page(
                id=created_page["id"],
                sourceId=created_page["sourceId"],
                imageUrl=created_page["imageUrl"],
                extractedText=created_page["extractedText"],
                title=created_page.get("title"),
                date=created_page.get("date"),
                notes=created_page.get("notes"),
                createdAt=created_page["createdAt"],
                updatedAt=created_page["updatedAt"]
            )
            
            created_pages.append(page_model)
        
        return PagesResponse(data=created_pages)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading multiple pages: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error uploading multiple pages: {str(e)}")
