# Search Result Source and Title Display

## Changes Made

- Modified the search results table in `frontend/src/pages/Search.tsx` to display the source and title of each search result
- Removed the image column from the search results table
- Added a source column that displays the source name with a link to the source detail page
- Added a title column that displays the page title or "Untitled" if no title is available
- Fixed JSX structure issues to ensure proper rendering

## Implementation Details

- Used the `sourceId` from each page to find the corresponding source in the search results
- Added a link to the source detail page for each source name
- Displayed "Unknown Source" if the source couldn't be found
- Displayed "Untitled" if the page doesn't have a title

## Result

The search results now show the source and title of each result, making it easier for users to identify and navigate to specific content in their archive.
