# Document Intelligence Endpoint Fix

## Changes Made

- Updated the .env file to use DOCUMENT_INTELLIGENCE_ENDPOINT instead of DOCUMENT_INTELLIGENCE_NAME
- Set the value of DOCUMENT_INTELLIGENCE_ENDPOINT to the full URL: https://konshareddocumentinteligence-eastus2.cognitiveservices.azure.com/

## Reason for Changes

The backend code in `backend/utils/document_intelligence.py` was looking for the environment variable DOCUMENT_INTELLIGENCE_ENDPOINT, but the .env file only had DOCUMENT_INTELLIGENCE_NAME defined. This was causing errors when trying to extract text from images, as seen in the logs.

By updating the .env file to use DOCUMENT_INTELLIGENCE_ENDPOINT with the full URL, we ensure that the Document Intelligence client can be properly initialized without having to modify the backend code.

## Impact

- The Document Intelligence functionality should now work correctly
- Text extraction from images should now function properly
- Error messages related to missing DOCUMENT_INTELLIGENCE_ENDPOINT should no longer appear in the logs
