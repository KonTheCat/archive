# AI Log - March 9, 2025 - OpenAI Proxy Fix (Second Attempt)

## Summary

Today I fixed an issue with the Azure OpenAI client initialization that was causing errors when trying to extract text from uploaded images. The error occurred because the OpenAI client was being passed an unexpected 'proxies' parameter.

## Issue

The error message was:

```
TypeError: Client.__init__() got an unexpected keyword argument 'proxies'
```

This error was occurring in the `VectorEmbeddingsHelper` class in `backend/utils/vector_embeddings.py` when initializing the AzureOpenAI client. The error was happening because the client was being passed a 'proxies' parameter that it doesn't accept.

## Fix

I modified the `VectorEmbeddingsHelper.__init__` method to create a custom HTTP client without proxies and pass it to the AzureOpenAI client. This approach follows the same pattern mentioned in a previous fix attempt.

The changes included:

1. Importing the httpx library:

   ```python
   import httpx
   ```

2. Creating a custom HTTP client without proxies:

   ```python
   http_client = httpx.Client()
   ```

3. Passing the custom HTTP client to the AzureOpenAI client constructor:
   ```python
   self.client = AzureOpenAI(
       api_version=self.api_version,
       azure_endpoint=self.api_endpoint,
       azure_ad_token=credential,
       http_client=http_client
   )
   ```

These changes ensure that the OpenAI client doesn't use any proxy configuration that might be present in the environment, which was causing the error.

## Result

With this fix, the application should now be able to properly extract text from uploaded images without encountering the proxy-related error. The text extraction process uses the vector embeddings helper to generate vector embeddings for the extracted text, which should now work correctly.

## Time: 2025-03-09 6:28:15 PM (America/New_York, UTC-4:00)
