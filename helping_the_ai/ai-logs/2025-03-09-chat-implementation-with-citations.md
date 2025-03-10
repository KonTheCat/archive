# Chat Implementation with Citations

## Changes Made

1. **Backend Changes**:

   - Created a new `chat.py` file in the `backend/v1` directory to implement the chat functionality using the Azure OpenAI API with the `gpt-4o` model.
   - Implemented a `ChatHelper` class that handles:
     - Initializing the Azure OpenAI client with identity-based authentication
     - Retrieving relevant context from the archive using vector search
     - Generating responses using the chat model
   - Added a `/chat` endpoint that accepts user messages and returns AI-generated responses
   - Implemented a citation system that tracks which sources were used to generate responses
   - Updated `routes.py` to include the chat router

2. **Frontend Changes**:
   - Updated the `types/index.ts` file to add chat-related types including Citation type
   - Added chat API functions to the `services/api.ts` file
   - Completely redesigned the `Chat.tsx` component to:
     - Maintain chat history (messages are persisted in the UI)
     - Implement the actual chat functionality using the backend API
     - Always use RAG (Retrieval Augmented Generation) for better responses
     - Display citations for each assistant message, showing which sources were used
     - Add a clear chat button with confirmation dialog

## Implementation Details

The chat functionality now uses the Azure OpenAI API with the `gpt-4o` model to generate responses. When a user sends a message, the following happens:

1. The message is sent to the backend `/chat` endpoint
2. The backend retrieves relevant context from the archive using vector embeddings
3. The backend generates a response using the chat model, incorporating the relevant context
4. The response is sent back to the frontend along with citations of the sources used
5. The frontend displays the response and provides a collapsible section showing the citations

The chat history is maintained in the UI, allowing users to see the conversation flow. Users can clear the chat history using the clear button in the top right corner, which shows a confirmation dialog before clearing.

## Citation System

The citation system provides transparency about which sources were used to generate the response:

1. When the backend retrieves relevant context using vector search, it also creates citation objects
2. Each citation includes:
   - Source ID and name
   - Page ID and title
   - A snippet of the text from that page
   - The similarity score (how relevant the system thinks this source is to the query)
3. These citations are returned to the frontend along with the response
4. The frontend displays a "Show sources" button that expands to show all the citations
5. This helps users understand where the information is coming from and verify its accuracy

This implementation provides a more transparent and trustworthy chat experience, as users can see exactly which parts of their archive were used to generate the response.
