# AI Log - March 9, 2025 - OpenAI Proxy Fix

## Summary

Today I fixed an issue with the Azure OpenAI client initialization that was causing errors when trying to extract text from uploaded images. The error occurred because the OpenAI client was being passed an unexpected 'proxies' parameter.

## Issue

The error message was:

```
TypeError: Client.__init__() got an unexpected keyword argument 'proxies'
```

This error was occurring in the `VectorEmbeddingsHelper` class in `backend/utils/vector_embeddings.py` when initializing the AzureOpenAI client. The error was happening because the client was being passed a 'proxies' parameter that it doesn't accept.

## Fix

I modified the `VectorEmbeddingsHelper.__init__` method to create a custom HTTP client without proxies and pass it to the AzureOpenAI client. This approach follows the same pattern used in other parts of the application to fix similar proxy-related issues.

The changes included:

1. For the Azure OpenAI client with DefaultAzureCredential:

   - Added code to create a token provider using `get_bearer_token_provider`
   - Created a custom HTTP client using `httpx.Client()`
   - Passed the custom HTTP client to the AzureOpenAI client constructor

2. For the Azure OpenAI client with API key:

   - Created a custom HTTP client using `httpx.Client()`
   - Passed the custom HTTP client to the AzureOpenAI client constructor

3. For the standard OpenAI client:
   - Created a custom HTTP client using `httpx.Client()`
   - Passed the custom HTTP client to the OpenAI client constructor

These changes ensure that the OpenAI clients don't use any proxy configuration that might be present in the environment, which was causing the error.

## Result

With this fix, the application should now be able to properly extract text from uploaded images without encountering the proxy-related error. The text extraction process uses the vector embeddings helper to generate vector embeddings for the extracted text, which is now working correctly.

## Time: 2025-03-09 6:17:45 PM (America/New_York, UTC-4:00)
