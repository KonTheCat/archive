# Text Extraction Error Handling Fix

## Issue

The application was encountering errors during the text extraction process when trying to update pages that no longer existed in the database. The error message was:

```
ValueError: Page with ID 12b9e493-80a1-43f1-bc5e-5bbe05e9d334 not found in source 885a0340-02cc-4024-9f92-b833db9e07a8
```

This occurred in the `extract_text_from_blob` function in `backend/v1/text_extraction.py` when it tried to update a page in Cosmos DB that didn't exist. The error was raised by the `update_page` method in `backend/utils/cosmos_db.py`.

## Changes Made

1. Modified the `extract_text_from_blob` function in `backend/v1/text_extraction.py` to:

   - Check if the page exists in Cosmos DB before attempting to extract text from the image
   - Add an early return with a warning log if the page doesn't exist
   - Add a second check before updating the page in case it was deleted during the text extraction process

2. Updated the page creation endpoints in `backend/v1/pages.py` to:
   - Verify that pages are fully created in Cosmos DB before scheduling text extraction
   - Skip text extraction and log an error if the page doesn't exist after creation
   - This was implemented in both the single page upload and multiple page upload endpoints

## Benefits

1. The application now gracefully handles cases where pages are deleted after text extraction is scheduled
2. Error logs are replaced with more informative warning logs
3. System resources aren't wasted processing text extraction for pages that no longer exist
4. Background tasks complete successfully instead of failing with errors
5. Text extraction is only scheduled when we can confirm the page exists in Cosmos DB

## Impact

These changes improve the robustness of the text extraction process in two ways:

1. By handling cases where pages are deleted after text extraction is scheduled
2. By ensuring pages are fully created in Cosmos DB before attempting to schedule text extraction

The application will now handle these edge cases gracefully without generating errors, leading to a more reliable text extraction process.
