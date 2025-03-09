from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import uvicorn
import logging
import sys
import datetime
from dotenv import load_dotenv
from backend.v1.routes import router as v1_router

# Load environment variables from .env file
load_dotenv()

# Configure logging
# Check if running in Azure App Service
is_azure_app_service = os.environ.get('WEBSITE_SITE_NAME') is not None

# Set up handlers
log_handlers = [logging.StreamHandler(sys.stdout)]  # Always log to stdout

# Add file handler if not running in Azure App Service
if not is_azure_app_service:
    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    # Create a timestamp for the log filename
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"{logs_dir}/server_{timestamp}.log"

    # Create file handler
    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    log_handlers.append(file_handler)

logging.basicConfig(
    level=logging.WARNING,  # Set to WARNING to capture unhandled errors by default
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=log_handlers
)
# Set up more detailed logging for our application modules
# Capture custom logs from our application
logging.getLogger('backend').setLevel(logging.INFO)
# Capture logs from this main module
logging.getLogger('__main__').setLevel(logging.INFO)

# Set third-party libraries to WARNING level to filter out their debug and info logs
logging.getLogger('azure').setLevel(logging.WARNING)
logging.getLogger('uvicorn').setLevel(logging.WARNING)
logging.getLogger('fastapi').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

logger.info("Starting AI Chat App")
logger.info("Environment variables loaded from .env file")

# Log whether file logging is enabled
if not is_azure_app_service:
    logger.info(
        f"File logging enabled. Logs will be written to {log_filename}")
else:
    logger.info("File logging disabled (running in Azure App Service)")

app = FastAPI(title="AI Chat App")

# Register API routers
app.include_router(v1_router, prefix="/api/v1")

# Check if the dist directory exists (where Vite builds the React app)
if not os.path.isdir("frontend/dist"):
    raise Exception(
        "React app not built. Run 'npm run build' in the frontend directory first.")

# Mount the static files from the React build
app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")


@app.get("/", include_in_schema=False)
async def serve_index():
    """Serve the React app's index.html for the root path."""
    return FileResponse("frontend/dist/index.html")


@app.get("/{catch_all:path}", include_in_schema=False)
async def serve_spa(catch_all: str):
    """
    Catch-all route to serve the React app's index.html for all paths.
    This enables client-side routing to work properly.
    """
    # If the path exists as a static file, serve it directly
    if os.path.isfile(f"frontend/dist/{catch_all}"):
        return FileResponse(f"frontend/dist/{catch_all}")

    # Otherwise, serve index.html to let the React app handle routing
    return FileResponse("frontend/dist/index.html")

if __name__ == "__main__":
    # Configure uvicorn logging
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["formatters"]["access"]["fmt"] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_config["formatters"]["default"]["fmt"] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Set uvicorn loggers to WARNING level to reduce noise
    log_config["loggers"]["uvicorn"]["level"] = "WARNING"
    log_config["loggers"]["uvicorn.error"]["level"] = "WARNING"
    log_config["loggers"]["uvicorn.access"]["level"] = "WARNING"

    # Run the application with logging configuration
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="warning",  # Changed from "info" to "warning"
        log_config=log_config
    )
