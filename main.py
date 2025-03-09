from fastapi import FastAPI
import uvicorn

from backend.v1.routes import router as v1_router

app = FastAPI(title="Archive")

app.include_router(v1_router, prefix="/api/v1")