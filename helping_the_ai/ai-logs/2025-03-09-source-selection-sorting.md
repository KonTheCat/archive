# Source Selection Sorting by Start Date

## Changes Made

Modified the SourceSelector component to sort sources by start date in the source selection dropdown. This ensures that sources are displayed in chronological order, making it easier for users to find and select sources based on their timeline.

### Implementation Details

1. Updated the `fetchSources` function in `SourceSelector.tsx` to sort the sources by start date after fetching them from the API.
2. Implemented a sorting algorithm that:
   - Places sources with a start date at the beginning, sorted from earliest to latest
   - Places sources without a start date at the end of the list
   - Maintains consistent ordering for sources with the same start date

### Benefits

- Improved user experience by presenting sources in a logical chronological order
- Makes it easier to find specific sources when there are many sources spanning different time periods
- Maintains the existing functionality while adding the sorting capability

The sorting is performed on the frontend side, requiring no changes to the backend API or database structure.
