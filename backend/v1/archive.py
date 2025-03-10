"""
This file is maintained for backward compatibility.
It re-exports components from the new modular files.
"""

from fastapi import APIRouter

from backend.v1.models import (
    SourceBase, SourceCreate, Source,
    PageBase, Page,
    SourceResponse, SourcesResponse,
    PageResponse, PagesResponse,
    SearchResponse
)

from backend.v1.sources import (
    get_sources,
    get_source,
    create_source
)

from backend.v1.pages import (
    get_pages,
    get_page,
    create_page,
    update_page,
    delete_page,
    upload_multiple_pages
)

from backend.v1.search import search

# Create a router that includes all the routes from the modular files
router = APIRouter()

# Re-export the routes
router.get("/sources", response_model=SourcesResponse)(get_sources)
router.get("/sources/{source_id}", response_model=SourceResponse)(get_source)
router.post("/sources", response_model=SourceResponse)(create_source)

router.get("/sources/{source_id}/pages", response_model=PagesResponse)(get_pages)
router.get("/sources/{source_id}/pages/{page_id}", response_model=PageResponse)(get_page)
router.post("/sources/{source_id}/pages", response_model=PageResponse)(create_page)
router.put("/sources/{source_id}/pages/{page_id}", response_model=PageResponse)(update_page)
router.delete("/sources/{source_id}/pages/{page_id}")(delete_page)
router.post("/sources/{source_id}/pages/upload", response_model=PagesResponse)(upload_multiple_pages)

router.get("/search", response_model=SearchResponse)(search)
