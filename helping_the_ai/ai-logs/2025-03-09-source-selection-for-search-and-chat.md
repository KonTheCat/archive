# Source Selection for Search and Chat

## Changes Made

1. **Created a Reusable Source Selector Component**:

   - Implemented a new `SourceSelector.tsx` component that allows users to select which sources to include in search and chat operations
   - Added a filter-by-title search box to easily find sources when there are many
   - Included source title and date range information in a compact, minimalist UI
   - Added "Select All" functionality with indeterminate state support
   - Made the component collapsible to save space when not in use
   - Set the component to start in the collapsed state by default

2. **Backend Changes**:

   - Updated the `/search` endpoint in `backend/v1/search.py` to accept an optional `source_ids` parameter
   - Modified the search queries to filter results by the selected sources
   - Updated the `/chat` endpoint in `backend/v1/chat.py` to accept an optional `source_ids` parameter
   - Modified the context retrieval logic to filter by selected sources

3. **Frontend API Service Updates**:

   - Enhanced the `searchApi.search()` function to accept and pass source IDs
   - Enhanced the `chatApi.sendMessage()` function to accept and pass source IDs

4. **Search Page Integration**:

   - Added the SourceSelector component to the search form
   - Updated the search form state to track selected sources
   - Modified the search API call to include selected source IDs

5. **Chat Page Integration**:
   - Added the SourceSelector component to the chat interface
   - Updated the chat state to track selected sources
   - Modified the chat API call to include selected source IDs

## Implementation Details

The source selection functionality defaults to selecting all sources when first loaded. Users can then:

- Filter sources by title using the search box
- Select or deselect individual sources
- Use the "Select All" checkbox to quickly select or deselect all sources
- See how many sources are currently selected out of the total

The component displays each source with its title and date range (start date to end date) in a compact format, making it easy to identify and select specific sources.

## Result

Users can now control which sources are included in both search and chat operations, allowing for more targeted and relevant results. This is particularly useful when users have many sources and want to focus on specific journals, documents, or time periods.
