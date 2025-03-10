# Page Upload and Background Task Fix

## Changes Made

### Frontend Fix:

Fixed an issue in `frontend/src/pages/SourceDetail.tsx` where newly uploaded pages were not immediately showing in the view of all pages in a source.

The problem was that when a new page was uploaded, the frontend was only adding the new page to the local state without refreshing the complete list from the backend. This could lead to inconsistencies, especially if there were any delays in the backend processing.

1. Modified the `handleFileChange` function (for single page upload) to fetch the complete list of pages from the backend after a successful upload, ensuring that the view is up-to-date.

2. Modified the `handleMultipleFileChange` function (for multiple page upload) to also fetch the complete list of pages after a successful upload.

3. Added fallback logic to both functions that will use the previous approach (adding to local state) if the refresh request fails, ensuring that the user still sees their uploaded pages even if there's an issue with the refresh.

### Backend Fix:

Fixed an issue in `backend/v1/pages.py` where background tasks for text extraction were not being properly scheduled.

The problem was that the `background_tasks` parameter in both the `create_page` and `upload_multiple_pages` functions had a default value of `None`, which meant that if FastAPI didn't inject a `BackgroundTasks` instance, the text extraction would not be scheduled.

1. Modified the `create_page` function to use `BackgroundTasks()` as the default value for the `background_tasks` parameter, ensuring that a `BackgroundTasks` instance is always available.

2. Modified the `upload_multiple_pages` function to also use `BackgroundTasks()` as the default value for the `background_tasks` parameter.

3. Removed the conditional checks `if background_tasks:` before scheduling text extraction, since we now ensure that `background_tasks` is always a valid instance.

These changes ensure that:

1. The page list is always up-to-date after an upload, showing all pages including newly uploaded ones.
2. Text extraction is properly scheduled as a background task for all uploaded pages.
