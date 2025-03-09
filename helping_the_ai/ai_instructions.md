## Personal Archive Project

This is intended to be a web application that stores images of pages from personal archive sources, such as journals. The following concepts need to be implemented:

1. The concept of a Source, this is something that contains Pages.
2. A Page has an associated image and textual information: the text extracted from the image, as well as metadata such as the date it was written, notes about it.
   a. Source ought to implement frontend and backend for uploading either one or many pages.
   b. In blob storage, the path to a given Page should be Source/Page.
3. There are to be 2 different ways of interacting with the content - search, which should look for string match in Cosmos DB content, and chat, which will implement RAG, details to come later.

Here are some technical details:

1.  The backend is implemented in FastAPI, the frontend is React/Vite in TypeScript.
2.  Make new files when adding net new functionality and import into existing structures.
3.  frontend/ is where the frontend is.
4.  backend/ is where the backend is.
5.  There is only a main.py at the root of the project, there is not an app.py anywhere or a main.py at the root of the backend/.
6.  Do not make any new folders without explicit approval.
7.  Run this command to rebuild the frontend: cd frontend && npm run build && cd ..
8.  Any resources mentioned in .env already exist.
9.  Prefer identity auth over key-based auth at all times.
10. I am a fan of how logging is done in helping_the_ai\main.py, but please configure that in a separate file in this project.
11. helping_the_ai\blob_storage.py and helping_the_ai\cosmos_db.py provide good examples of working with Blob Storage and Cosmos DB.
12. helping_the_ai\container_setup.py demonstrates setting up containers using the management package, this is how this should be done with identity auth.

Design notes:

1.  Prefer dark theme, clean Material Design. Probably a good idea to use Material UI.

## General Instructions:

1.  At the end of every action sequence, write a log entry to a file in helping_the_ai\ai-logs with a file name that reflects the current time, date and a few word summary of the changes. There should be a separate file for every change. The log entries should briefly but completely summarize the work that was done and the functionality that was accomplished.
2.  At the start of every action sequence, read the relevant recent ai_log files for this day to understand what is going on and what was done so far.
3.  In the root of the project there is folder called helping_the_ai. This contains useful context aids. In no case should the contents of that folder be modified. Content in helping_the_ai is to be used as reference only, nothing should be imported directly from this folder.
