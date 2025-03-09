from fastapi import APIRouter

from backend.v1.demo_background_task import router as demo_background_router

router = APIRouter()

router.include_router(demo_background_router, prefix="")