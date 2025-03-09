from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import uvicorn
from dotenv import load_dotenv
from backend.utils.logger import setup_logging, configure_uvicorn_logging

# Load environment variables from .env file
load_dotenv()

# Set up logging
logger = setup_logging("archive")

# Import routers
from backend.v1.routes import router as v1_router

# Import container setup
from backend.utils.cosmos_setup import setup_cosmos_containers

# Initialize Cosmos DB containers
try:
    logger.info("Setting up Cosmos DB containers...")
    setup_cosmos_containers()
    logger.info("Cosmos DB containers setup completed")
except Exception as e:
    logger.error(f"Error setting up Cosmos DB containers: {str(e)}")
    # Continue with application startup even if container setup fails
    # This allows the application to start even if there are issues with Cosmos DB

app = FastAPI(title="Archive")

# API routes
app.include_router(v1_router, prefix="/api/v1")

# Mount the static files from the frontend build
app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")

# Serve the frontend on the default route
@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    # If the path is empty or doesn't contain a dot (likely not a file), serve index.html
    if not full_path or "." not in full_path:
        return FileResponse("frontend/dist/index.html")
    
    # Otherwise, try to serve the requested file
    file_path = os.path.join("frontend/dist", full_path)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    
    # If the file doesn't exist, serve index.html for client-side routing
    return FileResponse("frontend/dist/index.html")

# Configure uvicorn logging if running directly
if __name__ == "__main__":
    uvicorn_log_config = configure_uvicorn_logging()
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="warning",
        log_config=uvicorn_log_config
    )
