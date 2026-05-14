from __future__ import annotations

import json
import logging
import os
from typing import Any

from openai import AsyncOpenAI

logger = logging.getLogger(__name__)

# Supported providers: "openai" (also covers DeepSeek, etc.) and "anthropic"
AI_PROVIDER = os.getenv("AI_PROVIDER", "openai")

SYSTEM_PROMPT = """You are an expert Excel and VBA macro developer. You help users create Excel files, 
dashboards, complex formulas, and VBA macros. You have deep knowledge of:

- Excel formulas (VLOOKUP, INDEX/MATCH, SUMIFS, array formulas, dynamic arrays, LAMBDA, LET, etc.)
- VBA macros and automation
- Dashboard design and data visualization
- Pivot tables and charts
- Conditional formatting
- Data validation
- Named ranges and structured references
- Power Query basics

When a user asks you to create an Excel file, you MUST respond with a JSON object containing the 
Excel file specification. Your response must be valid JSON with this structure:

{
    "action": "generate",
    "file_name": "descriptive_name.xlsx",
    "description": "Brief description of what was created",
    "sheets": [
        {
            "name": "Sheet1",
            "columns": [
                {"header": "Column A", "width": 15},
                {"header": "Column B", "width": 20}
            ],
            "data": [
                ["value1", "value2"],
                ["value3", "value4"]
            ],
            "formulas": [
                {"cell": "C2", "formula": "=A2+B2"},
                {"cell": "C3", "formula": "=A3+B3"}
            ],
            "formatting": {
                "header_color": "4472C4",
                "header_font_color": "FFFFFF",
                "alternate_row_color": "D9E2F3",
                "number_formats": {"B2:B100": "#,##0.00"}
            },
            "conditional_formatting": [
                {
                    "range": "C2:C100",
                    "type": "cell",
                    "criteria": ">",
                    "value": 100,
                    "format": {"bg_color": "92D050"}
                }
            ],
            "charts": [
                {
                    "type": "bar",
                    "title": "Chart Title",
                    "data_range": "A1:B10",
                    "position": "E2",
                    "x_axis": "Categories",
                    "y_axis": "Values"
                }
            ],
            "data_validation": [
                {
                    "range": "D2:D100",
                    "type": "list",
                    "values": ["Option1", "Option2", "Option3"]
                }
            ],
            "merge_cells": ["A1:D1"],
            "freeze_panes": "A2"
        }
    ],
    "vba_macros": [
        {
            "name": "MacroName",
            "code": "Sub MacroName()\\n    ' VBA code here\\nEnd Sub"
        }
    ],
    "named_ranges": [
        {"name": "RangeName", "sheet": "Sheet1", "range": "A2:A100"}
    ]
}

If the request is too complex to generate directly, or involves features that cannot be 
represented in a static Excel file (like real-time data connections, complex Power Query, etc.),
respond with:

{
    "action": "walkthrough",
    "description": "Brief explanation of why direct generation isn't possible",
    "steps": [
        "Step 1: ...",
        "Step 2: ...",
        "Step 3: ..."
    ],
    "tips": ["Helpful tip 1", "Helpful tip 2"],
    "partial_file": { ... }  // Optional: partial file spec if some parts can be generated
}

When modifying an existing file, respond with:

{
    "action": "modify",
    "file_name": "modified_name.xlsx",
    "description": "What was modified",
    "modifications": [
        {
            "sheet": "Sheet1",
            "add_columns": [{"header": "New Col", "width": 15}],
            "add_formulas": [{"cell": "E2", "formula": "=SUM(A2:D2)"}],
            "remove_columns": [],
            "add_formatting": {},
            "add_data": [],
            "add_charts": [],
            "add_conditional_formatting": [],
            "add_data_validation": []
        }
    ],
    "vba_macros": []
}

IMPORTANT RULES:
1. Always try to generate the file first. Only use walkthrough if truly impossible.
2. Make formulas dynamic and robust (use structured references where possible).
3. Include proper formatting to make files professional.
4. For dashboards, include charts, conditional formatting, and clean layouts.
5. Use realistic sample data when the user doesn't provide specific data.
6. Always respond with ONLY valid JSON - no markdown, no code blocks, just raw JSON.
7. For complex requests, break them into multiple sheets if needed.
8. Include VBA macros when the user specifically asks for automation/macros.
"""

MODIFY_SYSTEM_PROMPT = """You are an expert Excel analyst. You are given information about an 
existing Excel file and the user's instructions for modifying it. 

Analyze the file structure and respond with a JSON modification specification.
Your response must be valid JSON following the modification format.

When adding formulas, reference the actual column letters and row numbers based on the file structure.
When the user uploads a screenshot, use the visual information to understand the file layout.

IMPORTANT: Always respond with ONLY valid JSON - no markdown, no code blocks, just raw JSON.
"""


class AIEngine:
    def __init__(self) -> None:
        self.provider = os.getenv("AI_PROVIDER", "openai")
        self.client = None
        self.anthropic_client = None

        if self.provider == "anthropic":
            api_key = os.getenv("ANTHROPIC_API_KEY", "")
            if not api_key:
                logger.warning("ANTHROPIC_API_KEY not set - AI features will be unavailable")
            else:
                try:
                    import anthropic
                    self.anthropic_client = anthropic.AsyncAnthropic(api_key=api_key)
                except ImportError:
                    logger.error("anthropic package not installed: pip install anthropic")
            self.model = os.getenv("AI_MODEL", "claude-sonnet-4-20250514")
        else:
            api_key = os.getenv("OPENAI_API_KEY", "")
            base_url = os.getenv("OPENAI_BASE_URL", "") or None
            if not api_key:
                logger.warning("OPENAI_API_KEY not set - AI features will be unavailable")
            self.client = (
                AsyncOpenAI(api_key=api_key, base_url=base_url) if api_key else None
            )
            self.model = os.getenv("OPENAI_MODEL", "gpt-4o")

    @property
    def _is_available(self) -> bool:
        return self.client is not None or self.anthropic_client is not None

    async def _chat(
        self,
        system_prompt: str,
        messages: list[dict[str, Any]],
    ) -> str:
        if self.provider == "anthropic" and self.anthropic_client:
            response = await self.anthropic_client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.3,
                system=system_prompt,
                messages=messages,
            )
            return response.content[0].text
        elif self.client:
            all_messages: list[dict[str, Any]] = [
                {"role": "system", "content": system_prompt},
                *messages,
            ]
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=all_messages,
                temperature=0.3,
                max_tokens=4096,
                response_format={"type": "json_object"},
            )
            return response.choices[0].message.content or "{}"
        raise RuntimeError("No AI client available")

    async def generate_excel_spec(
        self,
        user_message: str,
        history: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        if not self._is_available:
            return self._fallback_response(user_message)

        messages: list[dict[str, Any]] = []

        if history:
            for msg in history:
                messages.append({"role": msg["role"], "content": msg["content"]})

        messages.append({"role": "user", "content": user_message})

        try:
            content = await self._chat(SYSTEM_PROMPT, messages)
            return self._parse_json(content)
        except json.JSONDecodeError:
            logger.error("Failed to parse AI response as JSON")
            return self._fallback_response(user_message)
        except Exception:
            logger.exception("AI engine error")
            return self._fallback_response(user_message)

    async def analyze_and_modify(
        self,
        file_summary: str,
        instructions: str,
        history: list[dict[str, str]] | None = None,
    ) -> dict[str, Any]:
        if not self._is_available:
            return self._fallback_modify_response(instructions)

        messages: list[dict[str, Any]] = []

        if history:
            for msg in history:
                messages.append({"role": msg["role"], "content": msg["content"]})

        prompt = (
            f"Here is the current Excel file structure:\n\n{file_summary}\n\n"
            f"User instructions: {instructions}"
        )
        messages.append({"role": "user", "content": prompt})

        try:
            content = await self._chat(MODIFY_SYSTEM_PROMPT, messages)
            return self._parse_json(content)
        except Exception:
            logger.exception("AI modify error")
            return self._fallback_modify_response(instructions)

    @staticmethod
    def _parse_json(text: str) -> dict[str, Any]:
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            lines = [l for l in lines if not l.strip().startswith("```")]
            text = "\n".join(lines)
        return json.loads(text)

    @staticmethod
    def _fallback_response(user_message: str) -> dict[str, Any]:
        return {
            "action": "walkthrough",
            "description": (
                "AI service is currently unavailable. Here's a general guide "
                "to help you achieve your goal."
            ),
            "steps": [
                "Open Microsoft Excel or Google Sheets",
                f"Based on your request: '{user_message[:100]}...'",
                "Create the required structure manually following Excel best practices",
                "Use the Formula bar to add complex formulas",
                "Format using Home > Styles for professional appearance",
            ],
            "tips": [
                "Use Ctrl+1 to quickly access cell formatting",
                "Press F4 to toggle absolute/relative references in formulas",
                "Use Alt+= for quick AutoSum",
            ],
        }

    @staticmethod
    def _fallback_modify_response(instructions: str) -> dict[str, Any]:
        return {
            "action": "walkthrough",
            "description": "AI service is currently unavailable.",
            "steps": [
                f"Open your Excel file and follow these instructions: {instructions[:200]}",
                "Navigate to the relevant sheet",
                "Make the requested changes manually",
                "Save the file when done",
            ],
            "tips": [
                "Use Ctrl+Z to undo if something goes wrong",
                "Save a backup copy before making major changes",
            ],
        }
