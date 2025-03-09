# AI Log - March 9, 2025 - Cosmos DB Setup Fix

## Summary

Today I fixed an error in the Cosmos DB container setup process. The error was occurring because the code was trying to access a non-existent environment variable.

## Issue

The error message was:

```
2025-03-09 17:56:00,028 - backend.utils.cosmos_setup - ERROR - Error setting up Cosmos DB containers: No value for given attribute
```

The issue was in `backend/utils/cosmos_setup.py` where the code was trying to access an environment variable called `COSMOSDB_ACCOUNT_NAME` which wasn't defined in the `.env` file. Instead, the `.env` file had a `COSMOS_DB_URL` variable which contained the URL to the Cosmos DB account.

## Fix

I modified the `cosmos_setup.py` file to extract the account name from the `COSMOS_DB_URL` environment variable using a regular expression pattern, similar to how it's done in `helping_the_ai/cosmos_db.py`. This approach is more robust as it derives the account name from the URL rather than requiring a separate environment variable.

The changes included:

1. Added the `re` module import for regular expression support
2. Replaced the direct access to `COSMOSDB_ACCOUNT_NAME` with code to extract it from `COSMOS_DB_URL`
3. Added a fallback to use `RESOURCE_GROUP` if `RG_NAME` is not available

The pattern used to extract the account name is:

```python
account_match = re.match(r'https://([^.]+)\.documents\.azure\.com', COSMOS_DB_URL)
if not account_match:
    raise ValueError(f"Invalid Cosmos DB URL format: {COSMOS_DB_URL}")

COSMOSDB_ACCOUNT_NAME = account_match.group(1)
```

This extracts the account name from URLs in the format `https://accountname.documents.azure.com:443/`.

## Result

With this fix, the application can now properly set up the Cosmos DB containers using the account name extracted from the URL, eliminating the need for a separate environment variable.

## Time: 2025-03-09 5:57:30 PM (America/New_York, UTC-4:00)
