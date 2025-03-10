# Multiple Page Upload Fix

## Issue

When trying to upload multiple pages at once, the following error occurred:

```
INFO:     127.0.0.1:49532 - "POST /api/v1/sources/57e470c1-3cff-44c9-b3f6-893e6875a592/pages/upload HTTP/1.1" 422 Unprocessable Entity
```

## Root Cause

The issue was in the frontend code for uploading multiple files. The frontend was appending files to the FormData object with indexed field names (`files[0]`, `files[1]`, etc.) and also adding separate `fileNames[0]`, `fileNames[1]`, etc. fields:

```javascript
files.forEach((file, index) => {
  formData.append(`files[${index}]`, file);
  formData.append(`fileNames[${index}]`, file.name);
});
```

However, the FastAPI backend endpoint expected a list of files with the same field name `files`:

```python
@router.post("/sources/{source_id}/pages/upload", response_model=PagesResponse)
async def upload_multiple_pages(
    source_id: str,
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
```

This mismatch in how the files were being sent vs. how they were expected caused the 422 Unprocessable Entity error.

## Solution

1. Modified the frontend code in `frontend/src/pages/SourceDetail.tsx` to correctly format the FormData for the backend endpoint:

```javascript
// Append each file with the same field name 'files'
// This matches the FastAPI expectation for List[UploadFile]
files.forEach((file) => {
  formData.append("files", file);
});
```

2. Added enhanced logging in the backend to better diagnose the issue:

```python
logger.info(f"Received {len(files)} files")

# Log file details for debugging
for i, file in enumerate(files):
    logger.info(f"File {i+1}: filename={file.filename}, content_type={file.content_type}, size={file.size if hasattr(file, 'size') else 'unknown'}")
```

3. Added error handling and logging in the frontend API service:

```javascript
try {
  // Log what we're sending for debugging
  console.log(`Uploading ${files.getAll("files").length} files to source ${sourceId}`);

  const response = await api.post<ApiResponse<Page[]>>(
    `/sources/${sourceId}/pages/upload`,
    files,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );
  return response.data;
} catch (error: any) {
  console.error("Error uploading multiple pages:", error);
  if (error.response) {
    console.error("Response data:", error.response.data);
    console.error("Response status:", error.response.status);
    console.error("Response headers:", error.response.headers);
  }
  throw error;
}
```

These changes ensure that all files are appended with the same field name `files`, which matches the FastAPI expectation for a `List[UploadFile]` parameter. The filename information is already included in the file object itself, so there's no need to send it separately. The additional logging helps diagnose any issues that might still occur.

## Time: 2025-03-09 9:21:00 PM (America/New_York, UTC-4:00)
