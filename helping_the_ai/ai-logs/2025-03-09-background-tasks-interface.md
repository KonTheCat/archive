# Background Tasks Interface Implementation

## Overview

Implemented a system to track, display, and manage background tasks in the application. This provides visibility into tasks that are currently pending on the server, such as text extraction processes, and allows users to cancel tasks if needed.

## Backend Changes

1. **Task Model**

   - Added `BackgroundTask` model in `backend/v1/models.py` to represent background tasks with properties like:
     - `id`: Unique identifier for the task
     - `taskType`: Type of task (e.g., "text_extraction")
     - `status`: Current status ("pending", "in_progress", "completed", "failed", "cancelled")
     - `sourceId`: Related source ID (optional)
     - `pageId`: Related page ID (optional)
     - `scheduledAt`: When the task was created
     - `canCancel`: Whether this task can be cancelled

2. **Task Manager**

   - Created `backend/v1/tasks.py` with an in-memory task store and functions to:
     - Register new tasks
     - Update task status
     - Retrieve tasks
     - Cancel tasks (individually or in bulk)

3. **API Endpoints**

   - Added REST endpoints for task management:
     - `GET /api/v1/tasks` - List all active tasks
     - `GET /api/v1/tasks/{task_id}` - Get details of a specific task
     - `DELETE /api/v1/tasks/{task_id}` - Cancel a specific task
     - `DELETE /api/v1/tasks` - Cancel multiple or all tasks

4. **Text Extraction Integration**
   - Modified `backend/v1/text_extraction.py` to register tasks when scheduling text extraction
   - Updated the extraction process to update task status as it progresses

## Frontend Changes

1. **Task Types**

   - Added `BackgroundTask` interface to `frontend/src/types/index.ts`

2. **API Service**

   - Extended `frontend/src/services/api.ts` with `tasksApi` functions to interact with the task endpoints

3. **Tasks Page**

   - Created `frontend/src/pages/Tasks.tsx` with:
     - Table view of all tasks
     - Status indicators using color-coded chips
     - Checkboxes for selecting tasks
     - Buttons for cancelling selected or all tasks
     - Auto-refresh functionality
     - Links to related sources and pages

4. **Navigation**
   - Added Tasks page to the application routes in `frontend/src/App.tsx`
   - Added Tasks entry to the navigation menu in `frontend/src/components/Layout.tsx`

## Dependencies

- Added `date-fns` package for date formatting in the Tasks page

## Benefits

1. **Visibility**: Users can now see what background tasks are running on the server
2. **Control**: Users can cancel pending tasks if needed
3. **Monitoring**: The status of text extraction and other background processes is now transparent
4. **Performance**: Users can identify if there are too many tasks running that might be affecting system performance

## Future Improvements

1. Consider adding task prioritization
2. Implement task queuing to limit concurrent tasks
3. Add more detailed task progress information
4. Persist task history for auditing purposes

## Time: 2025-03-09 9:42:00 PM (America/New_York, UTC-4:00)
