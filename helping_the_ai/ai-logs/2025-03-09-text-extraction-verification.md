# Text Extraction Verification Fix

## Changes Made

Fixed issues in `backend/v1/pages.py` to ensure that text extraction only proceeds if the page already exists in Cosmos DB and has been uploaded to blob storage:

1. Fixed duplicated code in the `create_page` function that was checking for page existence multiple times with nested if statements. Simplified to a single check.

2. Added a check in the `upload_multiple_pages` function to verify that the page exists in Cosmos DB before scheduling text extraction.

These changes ensure that text extraction is only attempted when:

1. The page has been successfully uploaded to blob storage
2. The page document has been successfully created in Cosmos DB

This prevents potential errors that could occur if text extraction was attempted on pages that don't exist in the database or haven't been properly uploaded to blob storage.
