import os
import re
import logging
import sys
import traceback
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from azure.cosmos import CosmosClient, exceptions as cosmos_exceptions
from azure.identity import AzureCliCredential, ManagedIdentityCredential, ChainedTokenCredential, CredentialUnavailableError
from azure.mgmt.cosmosdb import CosmosDBManagementClient
from azure.core.exceptions import ClientAuthenticationError, ResourceNotFoundError

# Get logger for this module
logger = logging.getLogger(__name__)

# Set up more detailed logging for Azure SDK
azure_logger = logging.getLogger('azure')
azure_logger.setLevel(logging.DEBUG)

# Custom JSON encoder to handle datetime objects


class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class CosmosDBClient:
    """Client for interacting with Azure Cosmos DB."""

    def __init__(self):
        """Initialize the Cosmos DB client using environment variables."""
        logger.info("Initializing CosmosDBClient")

        # Get environment variables
        self.cosmos_url = os.environ.get("COSMOS_DB_URL")
        self.database_name = os.environ.get("COSMOS_DB_DATABASE")
        self.subscription_id = os.environ.get("SUBSCRIPTION_ID")
        self.resource_group = os.environ.get("RESOURCE_GROUP")

        logger.info("Cosmos DB URL: %s", self.cosmos_url)
        logger.info("Database name: %s", self.database_name)
        logger.info("Subscription ID: %s", self.subscription_id)
        logger.info("Resource group: %s", self.resource_group)

        # Validate environment variables
        if not self.cosmos_url or not self.database_name:
            logger.error(
                "Missing required environment variables: COSMOS_DB_URL or COSMOS_DB_DATABASE")
            raise ValueError(
                "COSMOS_DB_URL and COSMOS_DB_DATABASE environment variables must be set")

        if not self.subscription_id or not self.resource_group:
            logger.error(
                "Missing required environment variables: SUBSCRIPTION_ID or RESOURCE_GROUP")
            raise ValueError(
                "SUBSCRIPTION_ID and RESOURCE_GROUP environment variables must be set")

        # Extract account name from URL (e.g., https://ai-chat.documents.azure.com:443/)
        account_match = re.match(
            r'https://([^.]+)\.documents\.azure\.com', self.cosmos_url)
        if not account_match:
            logger.error("Invalid Cosmos DB URL format: %s", self.cosmos_url)
            raise ValueError(
                f"Invalid Cosmos DB URL format: {self.cosmos_url}")

        self.account_name = account_match.group(1)
        logger.info("Extracted account name: %s", self.account_name)

        try:
            # Create a credential chain that first tries Azure CLI and then Managed Identity
            logger.info(
                "Creating credential chain with AzureCliCredential and ManagedIdentityCredential")
            self.credential = ChainedTokenCredential(
                AzureCliCredential(),
                ManagedIdentityCredential()
            )

            # Test the credential
            logger.info("Testing credential chain...")
            try:
                # Get a token to verify the credential works
                token = self.credential.get_token(
                    "https://management.azure.com/.default")
                logger.info(
                    "Successfully obtained token with credential chain")
                logger.info("Token expires on: %s", token.expires_on)
            except Exception as auth_error:
                logger.error(
                    "Failed to authenticate with credential chain: %s", str(auth_error))
                logger.error("Authentication error type: %s",
                             type(auth_error).__name__)
                logger.error("Authentication error traceback: %s",
                             traceback.format_exc())
                raise

            # Initialize the Cosmos DB client for data operations
            logger.info("Initializing CosmosClient")
            self.client = CosmosClient(
                self.cosmos_url, credential=self.credential)

            # Initialize the Cosmos DB management client for management operations
            logger.info("Initializing CosmosDBManagementClient")
            self.mgmt_client = CosmosDBManagementClient(
                credential=self.credential,
                subscription_id=self.subscription_id
            )

            # Ensure database and containers exist
            logger.info("Ensuring database exists")
            self._ensure_database_exists()

            logger.info("Ensuring containers exist")
            self._ensure_containers_exist()

            # Get database client
            logger.info("Getting database client for: %s", self.database_name)
            self.database = self.client.get_database_client(self.database_name)

            # Define container names
            self.chat_sessions_container_name = "chat_sessions"
            self.messages_container_name = "messages"
            self.spaces_container_name = "spaces"
            self.space_documents_container_name = "space_documents"
            self.user_settings_container_name = "user_settings"

            # Get container clients
            logger.info("Getting container client for: %s",
                        self.chat_sessions_container_name)
            self.chat_sessions_container = self.database.get_container_client(
                self.chat_sessions_container_name)

            logger.info("Getting container client for: %s",
                        self.messages_container_name)
            self.messages_container = self.database.get_container_client(
                self.messages_container_name)

            logger.info("Getting container client for: %s",
                        self.spaces_container_name)
            self.spaces_container = self.database.get_container_client(
                self.spaces_container_name)

            logger.info("Getting container client for: %s",
                        self.space_documents_container_name)
            self.space_documents_container = self.database.get_container_client(
                self.space_documents_container_name)

            logger.info("Getting container client for: %s",
                        self.user_settings_container_name)
            self.user_settings_container = self.database.get_container_client(
                self.user_settings_container_name)

            logger.info("CosmosDBClient initialization completed successfully")

        except Exception as e:
            logger.error("Error initializing CosmosDBClient: %s",
                         str(e), exc_info=True)
            raise

    def _ensure_database_exists(self):
        """Ensure that the database exists, create it if it doesn't."""
        try:
            # Check if database exists
            logger.info("Checking if database exists: %s", self.database_name)
            self.mgmt_client.sql_resources.get_sql_database(
                resource_group_name=self.resource_group,
                account_name=self.account_name,
                database_name=self.database_name
            )
            logger.info("Using existing database: %s", self.database_name)
        except Exception as e:
            # Create database if it doesn't exist
            logger.info("Database '%s' not found. Creating it...",
                        self.database_name)
            logger.debug("Error when checking for database: %s", str(e))

            try:
                database_params = {
                    "resource": {
                        "id": self.database_name
                    }
                }
                logger.info("Creating database with params: %s",
                            database_params)
                self.mgmt_client.sql_resources.begin_create_update_sql_database(
                    resource_group_name=self.resource_group,
                    account_name=self.account_name,
                    database_name=self.database_name,
                    create_update_sql_database_parameters=database_params
                ).result()
                logger.info("Database '%s' created successfully",
                            self.database_name)
            except Exception as create_error:
                logger.error("Failed to create database: %s",
                             str(create_error), exc_info=True)
                raise

    def _ensure_containers_exist(self):
        """Ensure that the required containers exist in the database."""
        # Define container configurations
        containers = [
            {
                "name": "chat_sessions",
                "partition_key_path": "/id"
            },
            {
                "name": "messages",
                "partition_key_path": "/sessionId"
            },
            {
                "name": "spaces",
                "partition_key_path": "/id"
            },
            {
                "name": "space_documents",
                "partition_key_path": "/spaceId"
            },
            {
                "name": "user_settings",
                "partition_key_path": "/userId"
            }
        ]

        logger.info("Checking and creating containers if needed")

        # Create containers if they don't exist
        for container in containers:
            container_name = container["name"]
            partition_key_path = container["partition_key_path"]

            try:
                # Check if container exists
                logger.info("Checking if container exists: %s", container_name)
                self.mgmt_client.sql_resources.get_sql_container(
                    resource_group_name=self.resource_group,
                    account_name=self.account_name,
                    database_name=self.database_name,
                    container_name=container_name
                )
                logger.info("Container '%s' already exists", container_name)
            except Exception as e:
                # Create container if it doesn't exist
                logger.info(
                    "Container '%s' not found. Creating it...", container_name)
                logger.debug("Error when checking for container: %s", str(e))

                try:
                    container_params = {
                        "resource": {
                            "id": container_name,
                            "partition_key": {
                                "paths": [partition_key_path]
                            }
                        }
                    }
                    logger.info(
                        "Creating container with params: %s", container_params)
                    self.mgmt_client.sql_resources.begin_create_update_sql_container(
                        resource_group_name=self.resource_group,
                        account_name=self.account_name,
                        database_name=self.database_name,
                        container_name=container_name,
                        create_update_sql_container_parameters=container_params
                    ).result()
                    logger.info(
                        "Container '%s' created successfully", container_name)
                except Exception as create_error:
                    logger.error("Failed to create container '%s': %s",
                                 container_name, str(create_error), exc_info=True)
                    raise

    # Chat Session Operations

    async def get_chat_sessions(self, user_id: Optional[str] = None, skip: int = 0, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get chat sessions, optionally filtered by user_id.
        Supports pagination with skip and limit parameters.
        Sessions are sorted by updatedAt in descending order (newest first).
        """
        if user_id:
            query = f"SELECT * FROM c WHERE c.userId = '{user_id}' ORDER BY c.updatedAt DESC OFFSET {skip} LIMIT {limit}"
        else:
            query = f"SELECT * FROM c ORDER BY c.updatedAt DESC OFFSET {skip} LIMIT {limit}"

        logger.info(f"Executing query: {query}")

        items = list(self.chat_sessions_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))

        logger.info(f"Retrieved {len(items)} chat sessions")
        return items

    async def get_chat_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a chat session by ID."""
        try:
            return self.chat_sessions_container.read_item(
                item=session_id,
                partition_key=session_id
            )
        except Exception:
            return None

    async def create_chat_session(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new chat session."""
        logger.info("=== COSMOS DB: CREATE CHAT SESSION ===")
        logger.info("Creating chat session: id=%s, userId=%s",
                    session.get('id', 'unknown'),
                    session.get('userId', 'unknown'))

        # Convert datetime objects to ISO format strings
        if 'createdAt' in session and isinstance(session['createdAt'], datetime):
            session['createdAt'] = session['createdAt'].isoformat()
        if 'updatedAt' in session and isinstance(session['updatedAt'], datetime):
            session['updatedAt'] = session['updatedAt'].isoformat()

        try:
            logger.info("Session data: %s", {
                'id': session.get('id', 'unknown'),
                'userId': session.get('userId', 'unknown'),
                'title': session.get('title', 'unknown'),
                'createdAt': session.get('createdAt', 'unknown'),
                'updatedAt': session.get('updatedAt', 'unknown')
            })

            result = self.chat_sessions_container.create_item(body=session)

            logger.info("Chat session created successfully: id=%s, userId=%s",
                        result.get('id', 'unknown'),
                        result.get('userId', 'unknown'))
            logger.info("=== COSMOS DB: CHAT SESSION CREATED SUCCESSFULLY ===")

            return result
        except cosmos_exceptions.CosmosHttpResponseError as e:
            logger.error("=== COSMOS DB: ERROR CREATING CHAT SESSION ===")
            logger.error("Cosmos DB HTTP Error: %s", str(e))
            logger.error("Status code: %s", e.status_code)
            logger.error("Sub status: %s", e.sub_status)
            logger.error("Error details: %s", e.http_error_message)
            logger.error("Request charge: %s", e.http_headers.get(
                'x-ms-request-charge', 'unknown'))
            logger.error("Activity ID: %s", e.http_headers.get(
                'x-ms-activity-id', 'unknown'))
            logger.error("Traceback: %s", traceback.format_exc())
            raise
        except Exception as e:
            logger.error("=== COSMOS DB: ERROR CREATING CHAT SESSION ===")
            logger.error(
                "Failed to create chat session in Cosmos DB: %s", str(e))
            logger.error("Error type: %s", type(e).__name__)
            logger.error("Traceback: %s", traceback.format_exc())
            raise

    async def update_chat_session(self, session_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing chat session."""
        # Get the current session
        session = await self.get_chat_session(session_id)
        if not session:
            raise ValueError(f"Chat session with ID {session_id} not found")

        # Convert datetime objects to ISO format strings
        for key, value in updates.items():
            if isinstance(value, datetime):
                updates[key] = value.isoformat()

        # Update the session with the new values
        for key, value in updates.items():
            session[key] = value

        # Save the updated session
        return self.chat_sessions_container.replace_item(
            item=session_id,
            body=session
        )

    async def delete_chat_session(self, session_id: str) -> None:
        """Delete a chat session and all its messages."""
        # Delete the session
        self.chat_sessions_container.delete_item(
            item=session_id,
            partition_key=session_id
        )

        # Delete all messages for this session
        query = f"SELECT * FROM c WHERE c.sessionId = '{session_id}'"
        messages = list(self.messages_container.query_items(
            query=query,
            partition_key=session_id
        ))

        for message in messages:
            self.messages_container.delete_item(
                item=message['id'],
                partition_key=session_id
            )

    # Message Operations

    async def get_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a chat session."""
        query = f"SELECT * FROM c WHERE c.sessionId = '{session_id}' ORDER BY c.timestamp ASC"
        items = list(self.messages_container.query_items(
            query=query,
            partition_key=session_id
        ))
        return items

    async def create_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new message."""
        logger.info("=== COSMOS DB: CREATE MESSAGE ===")

        # Ensure the message has a sessionId for partitioning
        if 'sessionId' not in message:
            logger.error("Message missing sessionId: %s", message)
            raise ValueError("Message must have a sessionId")

        logger.info("Creating message in Cosmos DB: role=%s, sessionId=%s, id=%s",
                    message.get('role', 'unknown'),
                    message.get('sessionId', 'unknown'),
                    message.get('id', 'unknown'))

        if 'content' in message:
            content_preview = message['content'][:50] + \
                '...' if len(message['content']) > 50 else message['content']
            logger.info("Message content preview: %s", content_preview)

        logger.info("Message container: %s", self.messages_container.id)
        logger.info("Database: %s", self.database.id)
        logger.info("Account: %s", self.account_name)

        try:
            # Convert datetime objects to ISO format strings
            # This is necessary because Cosmos DB doesn't accept datetime objects directly
            if 'timestamp' in message and isinstance(message['timestamp'], datetime):
                message['timestamp'] = message['timestamp'].isoformat()

            logger.info("Calling messages_container.create_item...")
            result = self.messages_container.create_item(body=message)
            logger.info("Message created successfully in Cosmos DB: id=%s",
                        result.get('id', 'unknown'))
            logger.info("Result from Cosmos DB: %s", {
                'id': result.get('id', 'unknown'),
                'role': result.get('role', 'unknown'),
                'sessionId': result.get('sessionId', 'unknown'),
                'timestamp': result.get('timestamp', 'unknown')
            })
            logger.info("=== COSMOS DB: MESSAGE CREATED SUCCESSFULLY ===")
            return result
        except cosmos_exceptions.CosmosHttpResponseError as e:
            logger.error("=== COSMOS DB: ERROR CREATING MESSAGE ===")
            logger.error("Cosmos DB HTTP Error: %s", str(e))
            logger.error("Status code: %s", e.status_code)
            logger.error("Sub status: %s", e.sub_status)
            logger.error("Error details: %s", e.http_error_message)
            logger.error("Request charge: %s", e.http_headers.get(
                'x-ms-request-charge', 'unknown'))
            logger.error("Activity ID: %s", e.http_headers.get(
                'x-ms-activity-id', 'unknown'))
            logger.error("Traceback: %s", traceback.format_exc())
            raise
        except Exception as e:
            logger.error("=== COSMOS DB: ERROR CREATING MESSAGE ===")
            logger.error("Failed to create message in Cosmos DB: %s", str(e))
            logger.error("Error type: %s", type(e).__name__)
            logger.error("Traceback: %s", traceback.format_exc())
            raise

    async def delete_messages(self, session_id: str) -> None:
        """Delete all messages for a chat session."""
        query = f"SELECT * FROM c WHERE c.sessionId = '{session_id}'"
        messages = list(self.messages_container.query_items(
            query=query,
            partition_key=session_id
        ))

        for message in messages:
            self.messages_container.delete_item(
                item=message['id'],
                partition_key=session_id
            )

    # Space Operations

    async def get_spaces(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all spaces, optionally filtered by user_id."""
        logger.info("=== COSMOS DB: GET SPACES ===")
        if user_id:
            query = f"SELECT * FROM c WHERE c.userId = '{user_id}' ORDER BY c.updatedAt DESC"
            logger.info(f"Executing query for user {user_id}: {query}")
        else:
            query = "SELECT * FROM c ORDER BY c.updatedAt DESC"
            logger.info("Executing query for all users: {query}")

        try:
            logger.info(
                f"Querying spaces container: {self.spaces_container.id}")
            items = list(self.spaces_container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            logger.info(f"Query successful, retrieved {len(items)} spaces")

            # Log space details for debugging
            for space in items:
                logger.info(
                    f"Space from Cosmos DB: ID={space.get('id', 'unknown')}, Name={space.get('name', 'unknown')}, UserId={space.get('userId', 'unknown')}")

            logger.info("=== COSMOS DB: GET SPACES SUCCESSFUL ===")
            return items
        except Exception as e:
            logger.error(f"Error querying spaces: {str(e)}", exc_info=True)
            logger.error("=== COSMOS DB: GET SPACES FAILED ===")
            raise

    async def get_space(self, space_id: str) -> Optional[Dict[str, Any]]:
        """Get a space by ID."""
        try:
            return self.spaces_container.read_item(
                item=space_id,
                partition_key=space_id
            )
        except Exception:
            return None

    async def create_space(self, space: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new space."""
        logger.info("=== COSMOS DB: CREATE SPACE ===")
        logger.info("Creating space: id=%s, name=%s",
                    space.get('id', 'unknown'),
                    space.get('name', 'unknown'))

        # Convert datetime objects to ISO format strings
        if 'createdAt' in space and isinstance(space['createdAt'], datetime):
            space['createdAt'] = space['createdAt'].isoformat()
        if 'updatedAt' in space and isinstance(space['updatedAt'], datetime):
            space['updatedAt'] = space['updatedAt'].isoformat()

        try:
            result = self.spaces_container.create_item(body=space)
            logger.info("Space created successfully: id=%s, name=%s",
                        result.get('id', 'unknown'),
                        result.get('name', 'unknown'))
            logger.info("=== COSMOS DB: SPACE CREATED SUCCESSFULLY ===")
            return result
        except Exception as e:
            logger.error("=== COSMOS DB: ERROR CREATING SPACE ===")
            logger.error("Failed to create space in Cosmos DB: %s", str(e))
            logger.error("Error type: %s", type(e).__name__)
            logger.error("Traceback: %s", traceback.format_exc())
            raise

    async def update_space(self, space_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing space."""
        # Get the current space
        space = await self.get_space(space_id)
        if not space:
            raise ValueError(f"Space with ID {space_id} not found")

        # Convert datetime objects to ISO format strings
        for key, value in updates.items():
            if isinstance(value, datetime):
                updates[key] = value.isoformat()

        # Update the space with the new values
        for key, value in updates.items():
            space[key] = value

        # Save the updated space
        return self.spaces_container.replace_item(
            item=space_id,
            body=space
        )

    async def delete_space(self, space_id: str) -> None:
        """Delete a space and all its documents."""
        # Delete the space
        self.spaces_container.delete_item(
            item=space_id,
            partition_key=space_id
        )

        # Delete all documents for this space
        query = f"SELECT * FROM c WHERE c.spaceId = '{space_id}'"
        documents = list(self.space_documents_container.query_items(
            query=query,
            partition_key=space_id
        ))

        for document in documents:
            self.space_documents_container.delete_item(
                item=document['id'],
                partition_key=space_id
            )

    # Space Document Operations

    async def get_space_documents(self, space_id: str) -> List[Dict[str, Any]]:
        """Get all documents for a space."""
        logger.info("=== COSMOS DB: GET SPACE DOCUMENTS ===")
        logger.info(f"Fetching documents for space ID: {space_id}")

        query = f"SELECT * FROM c WHERE c.spaceId = '{space_id}' ORDER BY c.updatedAt DESC"
        logger.info(f"Executing query: {query}")

        try:
            logger.info(
                f"Querying space_documents container: {self.space_documents_container.id}")
            items = list(self.space_documents_container.query_items(
                query=query,
                partition_key=space_id
            ))
            logger.info(
                f"Query successful, retrieved {len(items)} documents for space {space_id}")

            # Log document details for debugging
            for doc in items:
                logger.info(
                    f"Document from Cosmos DB: ID={doc.get('id', 'unknown')}, Title={doc.get('title', 'unknown')}, SpaceId={doc.get('spaceId', 'unknown')}")

            logger.info("=== COSMOS DB: GET SPACE DOCUMENTS SUCCESSFUL ===")
            return items
        except Exception as e:
            logger.error(
                f"Error querying space documents: {str(e)}", exc_info=True)
            logger.error("=== COSMOS DB: GET SPACE DOCUMENTS FAILED ===")
            raise

    async def get_space_document(self, space_id: str, document_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID."""
        try:
            return self.space_documents_container.read_item(
                item=document_id,
                partition_key=space_id
            )
        except Exception:
            return None

    async def create_space_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new document."""
        logger.info("=== COSMOS DB: CREATE SPACE DOCUMENT ===")

        # Ensure the document has a spaceId for partitioning
        if 'spaceId' not in document:
            logger.error("Document missing spaceId: %s", document)
            raise ValueError("Document must have a spaceId")

        logger.info("Creating document: id=%s, title=%s, spaceId=%s",
                    document.get('id', 'unknown'),
                    document.get('title', 'unknown'),
                    document.get('spaceId', 'unknown'))

        # Convert datetime objects to ISO format strings
        if 'createdAt' in document and isinstance(document['createdAt'], datetime):
            document['createdAt'] = document['createdAt'].isoformat()
        if 'updatedAt' in document and isinstance(document['updatedAt'], datetime):
            document['updatedAt'] = document['updatedAt'].isoformat()

        try:
            result = self.space_documents_container.create_item(body=document)
            logger.info("Document created successfully: id=%s, title=%s",
                        result.get('id', 'unknown'),
                        result.get('title', 'unknown'))
            logger.info(
                "=== COSMOS DB: SPACE DOCUMENT CREATED SUCCESSFULLY ===")
            return result
        except Exception as e:
            logger.error("=== COSMOS DB: ERROR CREATING SPACE DOCUMENT ===")
            logger.error("Failed to create document in Cosmos DB: %s", str(e))
            logger.error("Error type: %s", type(e).__name__)
            logger.error("Traceback: %s", traceback.format_exc())
            raise

    async def update_space_document(self, space_id: str, document_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing document."""
        # Get the current document
        document = await self.get_space_document(space_id, document_id)
        if not document:
            raise ValueError(
                f"Document with ID {document_id} not found in space {space_id}")

        # Convert datetime objects to ISO format strings
        for key, value in updates.items():
            if isinstance(value, datetime):
                updates[key] = value.isoformat()

        # Update the document with the new values
        for key, value in updates.items():
            document[key] = value

        # Save the updated document
        return self.space_documents_container.replace_item(
            item=document_id,
            body=document
        )

    async def delete_space_document(self, space_id: str, document_id: str) -> None:
        """Delete a document."""
        self.space_documents_container.delete_item(
            item=document_id,
            partition_key=space_id
        )

    # User Settings Operations

    async def get_user_settings(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user settings by user ID."""
        try:
            query = f"SELECT * FROM c WHERE c.userId = '{user_id}'"
            items = list(self.user_settings_container.query_items(
                query=query,
                partition_key=user_id
            ))
            return items[0] if items else None
        except Exception as e:
            logger.error("Error getting user settings: %s",
                         str(e), exc_info=True)
            return None

    async def create_user_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Create new user settings."""
        logger.info("=== COSMOS DB: CREATE USER SETTINGS ===")

        # Ensure the settings has a userId for partitioning
        if 'userId' not in settings:
            logger.error("Settings missing userId: %s", settings)
            raise ValueError("Settings must have a userId")

        logger.info("Creating user settings: userId=%s",
                    settings.get('userId', 'unknown'))

        try:
            result = self.user_settings_container.create_item(body=settings)
            logger.info("User settings created successfully: userId=%s",
                        result.get('userId', 'unknown'))
            logger.info(
                "=== COSMOS DB: USER SETTINGS CREATED SUCCESSFULLY ===")
            return result
        except Exception as e:
            logger.error("=== COSMOS DB: ERROR CREATING USER SETTINGS ===")
            logger.error(
                "Failed to create user settings in Cosmos DB: %s", str(e))
            logger.error("Error type: %s", type(e).__name__)
            logger.error("Traceback: %s", traceback.format_exc())
            raise

    async def update_user_settings(self, user_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update existing user settings or create if they don't exist."""
        # Try to get existing settings
        settings = await self.get_user_settings(user_id)

        if settings:
            # Update existing settings
            for key, value in updates.items():
                settings[key] = value

            # Add updatedAt timestamp if not already in updates
            if 'updatedAt' not in updates:
                settings['updatedAt'] = datetime.now().isoformat()

            # Log the update operation
            logger.info("=== COSMOS DB: UPDATE USER SETTINGS ===")
            logger.info(f"Updating settings for user: {user_id}")
            logger.info(f"Document ID: {settings.get('id')}")
            logger.info(f"Updates: {updates}")

            try:
                # Save the updated settings using upsert_item
                result = self.user_settings_container.upsert_item(
                    body=settings
                )
                logger.info("User settings updated successfully")
                return result
            except Exception as e:
                logger.error(
                    f"Error updating user settings: {str(e)}", exc_info=True)
                raise
        else:
            # Create new settings
            new_settings = {
                'id': user_id,  # Use user_id as the document id
                'userId': user_id,
                **updates,
                'createdAt': datetime.now().isoformat(),
                'updatedAt': datetime.now().isoformat()
            }
            return await self.create_user_settings(new_settings)


# Create a singleton instance
cosmos_db_client = None


def get_cosmos_db_client() -> CosmosDBClient:
    """Get or create the CosmosDBClient singleton."""
    global cosmos_db_client
    if cosmos_db_client is None:
        cosmos_db_client = CosmosDBClient()
    return cosmos_db_client
