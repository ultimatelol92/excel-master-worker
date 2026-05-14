from __future__ import annotations

import json
import logging
import uuid

from fastapi import APIRouter

from app.models.schemas import ChatRequest, ChatResponse, FileAction
from app.services.ai_engine import AIEngine
from app.services.excel_generator import ExcelGenerator
from app.services.file_analyzer import FileAnalyzer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])

ai_engine = AIEngine()
excel_gen = ExcelGenerator()
file_analyzer = FileAnalyzer()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    conversation_id = request.conversation_id or str(uuid.uuid4())

    history = [{"role": m.role.value, "content": m.content} for m in request.history]

    user_message = request.message
    if request.uploaded_file_id:
        file_path = ExcelGenerator.get_uploaded_file_path(request.uploaded_file_id)
        if file_path:
            summary = file_analyzer.get_file_summary_text(file_path)
            user_message = (
                f"{request.message}\n\n"
                f"[Attached Excel file analysis]:\n{summary}"
            )

    spec = await ai_engine.generate_excel_spec(user_message, history)

    action = spec.get("action", "generate")

    if action == "generate":
        try:
            file_id, file_name = excel_gen.generate_from_spec(spec)
            return ChatResponse(
                message=spec.get("description", "Your Excel file has been generated!"),
                action=FileAction.GENERATE,
                file_url=f"/api/files/download/{file_id}",
                file_name=file_name,
                conversation_id=conversation_id,
            )
        except Exception:
            logger.exception("Failed to generate Excel file")
            return ChatResponse(
                message="I encountered an error generating the file. Let me provide a walkthrough instead.",
                action=FileAction.WALKTHROUGH,
                conversation_id=conversation_id,
                walkthrough_steps=spec.get("steps", ["Please try again with more details."]),
            )

    elif action == "modify":
        if not request.uploaded_file_id:
            return ChatResponse(
                message="Please upload an Excel file first so I can modify it.",
                action=FileAction.WALKTHROUGH,
                conversation_id=conversation_id,
                walkthrough_steps=[
                    "Click the upload button to attach your Excel file",
                    "Then describe the modifications you'd like",
                ],
            )
        try:
            file_id, file_name = excel_gen.modify_file(request.uploaded_file_id, spec)
            return ChatResponse(
                message=spec.get("description", "Your file has been modified!"),
                action=FileAction.MODIFY,
                file_url=f"/api/files/download/{file_id}",
                file_name=file_name,
                conversation_id=conversation_id,
            )
        except Exception:
            logger.exception("Failed to modify file")
            return ChatResponse(
                message="I had trouble modifying the file. Here's a manual guide:",
                action=FileAction.WALKTHROUGH,
                conversation_id=conversation_id,
                walkthrough_steps=spec.get("steps", ["Please try again."]),
            )

    else:
        steps = spec.get("steps", [])
        tips = spec.get("tips", [])
        full_steps = steps + (["\n--- Tips ---"] + tips if tips else [])

        partial = spec.get("partial_file")
        file_url = None
        file_name = None
        if partial and partial.get("sheets"):
            try:
                file_id, file_name = excel_gen.generate_from_spec(partial)
                file_url = f"/api/files/download/{file_id}"
            except Exception:
                logger.warning("Failed to generate partial file")

        return ChatResponse(
            message=spec.get("description", "Here's a walkthrough to achieve your goal:"),
            action=FileAction.WALKTHROUGH,
            file_url=file_url,
            file_name=file_name,
            conversation_id=conversation_id,
            walkthrough_steps=full_steps,
        )
