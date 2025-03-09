from fastapi import APIRouter

from backend.v1.demo_background_task import router as demo_background_router
from backend.v1.archive import router as archive_router

router = APIRouter()

router.include_router(demo_background_router, prefix="")
router.include_router(archive_router, prefix="")
