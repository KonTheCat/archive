# Source Start and End Dates Implementation

Added start and end dates to the source model, making them editable on both the frontend and backend.

## Changes Made

### Backend Changes

1. Updated the `SourceBase` model in `models.py` to include optional `startDate` and `endDate` fields.
2. Modified the `sources.py` API endpoints to handle the new fields:
   - Updated the `get_sources` and `get_source` methods to include the new fields in the response.
   - Updated the `create_source` method to accept and store the new fields.
   - Added a `update_source` endpoint to allow editing the source, including the new date fields.

### Frontend Changes

1. Updated the `Source` and `SourceCreate` interfaces in `types/index.ts` to include the optional `startDate` and `endDate` fields.
2. Modified the `Sources.tsx` component to:
   - Display the start and end dates in the sources table.
   - Add date input fields to the create source dialog.
   - Update the create source handler to include the new fields.
3. Modified the `SourceDetail.tsx` component to:
   - Display the start and end dates in the source details.
   - Add date input fields to the edit source dialog.
   - Update the edit source handler to include the new fields.

## Result

Users can now specify start and end dates for sources, which are displayed in the source list and detail views, and can be edited through the UI.
