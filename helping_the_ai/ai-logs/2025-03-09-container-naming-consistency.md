# Container Naming Consistency and Code Cleanup

## Changes Made

1. **Inconsistent Container Naming**:

   - Updated all instances of "spaceId" to "sourceId" in backend/v1/pages.py to match the container names defined in cosmos_setup.py ("sources" and "pages").
   - This ensures consistency across the codebase and makes it easier to understand and maintain.

2. **Method Name Consistency**:

   - Changed `update_space_document` to `update_page` in backend/v1/text_extraction.py to maintain consistent naming conventions.
   - This aligns with the container naming scheme and other method names in the codebase.

3. **Demo Code Removal**:
   - The demo_background_task.py file has been removed as it was just placeholder code.

These changes ensure that the codebase follows consistent naming conventions and removes unnecessary demo code, making the project more maintainable and easier to understand.

## Next Steps

- The RAG chat functionality in frontend/src/pages/Chat.tsx has been left as is for now, as it will be revisited later.
