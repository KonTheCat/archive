import logging
import os
import sys
import datetime
import uvicorn

# Configure logging
def setup_logging(app_name="archive"):
    """
    Set up logging configuration for the application.
    
    Args:
        app_name (str): The name of the application for logging purposes.
        
    Returns:
        logging.Logger: A configured logger instance.
    """
    # Check if running in Azure App Service
    is_azure_app_service = os.environ.get('WEBSITE_SITE_NAME') is not None

    # Set up handlers
    log_handlers = [logging.StreamHandler(sys.stdout)]  # Always log to stdout

    # Add file handler if not running in Azure App Service
    log_filename = None
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

    # Configure basic logging
    logging.basicConfig(
        level=logging.WARNING,  # Set to WARNING to capture unhandled errors by default
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=log_handlers
    )
    
    # Set up more detailed logging for our application modules
    # Capture custom logs from our application
    logging.getLogger('backend').setLevel(logging.INFO)
    # Capture logs from main module
    logging.getLogger('__main__').setLevel(logging.INFO)

    # Set third-party libraries to WARNING level to filter out their debug and info logs
    # Azure SDK has multiple loggers, set them all to WARNING
    logging.getLogger('azure').setLevel(logging.WARNING)
    logging.getLogger('azure.core').setLevel(logging.WARNING)
    logging.getLogger('azure.identity').setLevel(logging.WARNING)
    logging.getLogger('azure.cosmos').setLevel(logging.WARNING)
    logging.getLogger('azure.storage').setLevel(logging.WARNING)
    logging.getLogger('msal').setLevel(logging.WARNING)
    
    # Set other third-party libraries to WARNING level
    logging.getLogger('uvicorn').setLevel(logging.WARNING)
    logging.getLogger('fastapi').setLevel(logging.WARNING)

    # Create and configure logger for the caller
    logger = logging.getLogger(app_name)
    logger.setLevel(logging.INFO)

    # Log whether file logging is enabled
    if not is_azure_app_service and log_filename:
        logger.info(f"File logging enabled. Logs will be written to {log_filename}")
    else:
        logger.info("File logging disabled (running in Azure App Service)")

    return logger

def get_logger(module_name):
    """
    Get a logger for a specific module.
    
    Args:
        module_name (str): The name of the module requesting the logger.
        
    Returns:
        logging.Logger: A configured logger instance for the module.
    """
    logger = logging.getLogger(module_name)
    return logger

def configure_uvicorn_logging():
    """
    Configure Uvicorn logging settings.
    
    Returns:
        dict: Uvicorn logging configuration dictionary.
    """
    log_config = uvicorn.config.LOGGING_CONFIG.copy()
    log_config["formatters"]["access"]["fmt"] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_config["formatters"]["default"]["fmt"] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Set uvicorn loggers to WARNING level to reduce noise
    log_config["loggers"]["uvicorn"]["level"] = "WARNING"
    log_config["loggers"]["uvicorn.error"]["level"] = "WARNING"
    log_config["loggers"]["uvicorn.access"]["level"] = "WARNING"
    
    return log_config
