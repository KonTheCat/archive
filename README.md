# Personal Archive

A web application for storing, searching, and interacting with personal archive sources such as journals, documents, and other text-based materials.

## Overview

Personal Archive is an AI-powered application that allows you to:

- Upload and organize personal archive sources (journals, documents, etc.)
- Extract and store text from document images
- Search through your archive with powerful text search
- Chat with your archive using AI-powered retrieval augmented generation (RAG)
- Manage background tasks for document processing

**Note: This application is almost entirely AI-generated.**

## Features

### Source Management

- Create and manage archive sources (journals, documents, etc.)
- Upload single or multiple pages to sources
- View source details including date ranges

### Page Management

- View page details including extracted text
- Upload page images
- Automatic text extraction from images

### Search

- Full-text search across your entire archive
- Filter search by specific sources
- View search results with source and title information
- Context highlighting in search results

### AI Chat

- Chat with your archive using RAG technology
- View citations for AI-generated responses
- Filter chat by specific sources
- Transparent source attribution

### Background Tasks

- Monitor text extraction and other background tasks
- Cancel pending tasks
- Track task status and progress

## Technology Stack

### Frontend

- React with TypeScript
- Vite for build tooling
- Material UI for component library
- React Router for navigation

### Backend

- FastAPI (Python)
- Azure Blob Storage for document storage
- Azure Cosmos DB for metadata and text storage
- Azure Document Intelligence for text extraction
- Azure OpenAI for chat functionality

## Project Structure

```
├── backend/
│   ├── utils/           # Utility functions for Azure services
│   └── v1/              # API version 1 implementation
├── frontend/
│   ├── public/          # Static assets
│   └── src/
│       ├── assets/      # Frontend assets
│       ├── components/  # Reusable React components
│       ├── pages/       # Page components
│       ├── services/    # API service functions
│       ├── types/       # TypeScript type definitions
│       └── utils/       # Frontend utility functions
├── .env                 # Environment variables
├── main.py              # Application entry point
└── requirements.txt     # Python dependencies
```

## Setup and Installation

### Prerequisites

- Node.js and npm
- Python 3.8+
- Azure account with the following services:
  - Blob Storage
  - Cosmos DB
  - Document Intelligence
  - OpenAI

### Backend Setup

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Unix/MacOS: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Configure environment variables in `.env` file (see Environment Variables section below)

### Frontend Setup

1. Navigate to the frontend directory: `cd frontend`
2. Install dependencies: `npm install`
3. Build the frontend: `npm run build`

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```
# Azure Storage
STORAGE_ACCOUNT_NAME = your_storage_account_name
STORAGE_CONTAINER_NAME = your_container_name
SUBSCRIPTION_ID = "your_subscription_id"
RG_NAME = "your_resource_group_name"
LOCATION = "your_azure_region"

# Azure Document Intelligence
DOCUMENT_INTELLIGENCE_ENDPOINT = your_document_intelligence_endpoint

# Azure OpenAI
AZURE_OPENAI_ENDPOINT = your_openai_endpoint
AOAI_EMBEDDING_DEPLOYMENT = your_embedding_model_deployment_name
AOAI_CHAT_DEPLOYMENT = your_chat_model_deployment_name

# Azure Cosmos DB
COSMOS_DB_URL = your_cosmos_db_url
COSMOS_DB_DATABASE = your_database_name
RESOURCE_GROUP = "your_resource_group_name"
```

Note: The application uses Azure identity-based authentication, so make sure you're logged in with the Azure CLI or have the appropriate credentials configured.

### Running the Application

1. Start the backend server: `python main.py`
2. Access the application at `http://localhost:8000`

## Usage

### Adding a Source

1. Navigate to the Sources page
2. Click "Add Source"
3. Enter source details and save

### Uploading Pages

1. Navigate to a source detail page
2. Click "Upload Pages"
3. Select single or multiple page images to upload
4. Wait for text extraction to complete

### Searching

1. Navigate to the Search page
2. Enter search terms
3. Optionally filter by specific sources
4. View and explore search results

### Chatting with Your Archive

1. Navigate to the Chat page
2. Optionally select specific sources to include
3. Enter your question or prompt
4. View the AI-generated response with source citations

### Managing Tasks

1. Navigate to the Tasks page
2. View current background tasks
3. Cancel tasks if needed

## License

[Your License Here]
