from fastapi import APIRouter

from backend.v1.sources import router as sources_router
from backend.v1.pages import router as pages_router
from backend.v1.search import router as search_router
from backend.v1.chat import router as chat_router

router = APIRouter()

router.include_router(sources_router, prefix="")
router.include_router(pages_router, prefix="")
router.include_router(search_router, prefix="")
router.include_router(chat_router, prefix="")
