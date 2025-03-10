# Chat Usage Information

## Changes Made

1. **Backend Changes**:

   - Updated the `chat.py` file to include usage information in the chat response
   - Added a new `UsageInfo` Pydantic model to represent token usage data
   - Modified the `generate_response` method to return both the response text and usage information
   - Updated the chat endpoint to include usage information in the response

2. **Frontend Changes**:
   - Added a new `UsageInfo` interface in `types/index.ts`
   - Updated the `ApiResponse` interface to include optional usage information
   - Created a new `UsageInfoDisplay` component in `Chat.tsx` to display token usage
   - Modified the chat UI to show usage information for each assistant message

## Implementation Details

The chat functionality now includes token usage information from the Azure OpenAI API. When a user sends a message, the following happens:

1. The backend retrieves the usage information from the OpenAI API response
2. The usage information is included in the response sent back to the frontend
3. The frontend displays the usage information in a collapsible section below each assistant message

The usage information includes:

- Prompt tokens: The number of tokens used in the prompt (system message + user message + context)
- Completion tokens: The number of tokens used in the assistant's response
- Total tokens: The sum of prompt and completion tokens

This implementation provides transparency about the token usage for each chat interaction, which can be useful for monitoring API usage and costs.

## User Interface

The usage information is displayed in a collapsible section similar to the citations. Users can click "Show usage info" to expand the section and see the token counts. This keeps the interface clean while still providing access to the detailed usage information when needed.
