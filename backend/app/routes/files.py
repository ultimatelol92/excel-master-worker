from __future__ import annotations

import logging
import os

from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.models.schemas import FileModifyRequest, FileModifyResponse, FileUploadResponse
from app.services.ai_engine import AIEngine
from app.services.excel_generator import ExcelGenerator
from app.services.file_analyzer import FileAnalyzer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/files", tags=["files"])

ai_engine = AIEngine()
excel_gen = ExcelGenerator()
file_analyzer = FileAnalyzer()

ALLOWED_EXTENSIONS = {".xlsx", ".xlsm", ".xls", ".csv"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile) -> FileUploadResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 50MB)")

    file_id, file_path = file_analyzer.save_upload(content, file.filename)

    try:
        analysis = file_analyzer.analyze_file(file_path)
        summary = file_analyzer.get_file_summary_text(file_path)

        return FileUploadResponse(
            file_id=file_id,
            file_name=file.filename,
            sheet_names=analysis["sheet_names"],
            summary=summary,
        )
    except Exception:
        logger.exception("Failed to analyze uploaded file")
        raise HTTPException(status_code=400, detail="Failed to analyze the uploaded file. Is it a valid Excel file?")


@router.get("/download/{file_id}")
async def download_file(file_id: str) -> FileResponse:
    file_path = ExcelGenerator.get_generated_file_path(file_id)
    if not file_path:
        file_path = ExcelGenerator.get_uploaded_file_path(file_id)
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    actual_name = "_".join(os.path.basename(file_path).split("_")[1:])
    return FileResponse(
        path=file_path,
        filename=actual_name,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@router.post("/modify", response_model=FileModifyResponse)
async def modify_file(request: FileModifyRequest) -> FileModifyResponse:
    file_path = ExcelGenerator.get_uploaded_file_path(request.file_id)
    if not file_path:
        raise HTTPException(status_code=404, detail="Uploaded file not found")

    summary = file_analyzer.get_file_summary_text(file_path)
    history = [{"role": m.role.value, "content": m.content} for m in request.history]

    modifications = await ai_engine.analyze_and_modify(summary, request.instructions, history)

    action = modifications.get("action", "modify")

    if action == "walkthrough":
        return FileModifyResponse(
            message=modifications.get("description", "Here's how to make these changes:"),
            walkthrough_steps=modifications.get("steps", []),
        )

    try:
        new_file_id, new_file_name = excel_gen.modify_file(request.file_id, modifications)
        return FileModifyResponse(
            message=modifications.get("description", "Your file has been modified!"),
            file_url=f"/api/files/download/{new_file_id}",
            file_name=new_file_name,
        )
    except Exception:
        logger.exception("Failed to modify file")
        return FileModifyResponse(
            message="I had trouble modifying the file directly. Here are manual instructions:",
            walkthrough_steps=[
                "Open the file in Excel",
                f"Follow these modifications: {request.instructions}",
                "Save the file when done",
            ],
        )


@router.post("/upload-image")
async def upload_image(file: UploadFile) -> dict[str, str]:
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp"}:
        raise HTTPException(status_code=400, detail="Unsupported image format")

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image too large (max 10MB)")

    import uuid
    image_id = str(uuid.uuid4())
    uploads_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
    os.makedirs(uploads_dir, exist_ok=True)
    image_path = os.path.join(uploads_dir, f"{image_id}_{file.filename}")

    with open(image_path, "wb") as f:
        f.write(content)

    return {
        "image_id": image_id,
        "message": "Image uploaded. Please describe what you'd like me to do with this Excel file screenshot.",
    }
