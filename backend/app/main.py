from __future__ import annotations

import logging
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.models.schemas import HealthResponse
from app.routes import chat, files

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

app = FastAPI(
    title="Excel Master Worker",
    description="AI-powered Excel/Macro generator and assistant",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(files.router)

frontend_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")


@app.get("/api/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return HealthResponse(status="healthy", version="1.0.0")
