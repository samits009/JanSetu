import os
import json
import asyncio
import logging
from typing import Dict, Any, List, Type, Optional
from pydantic import BaseModel
from .base import AIProvider
from app.agents.tools import ToolDefinition

logger = logging.getLogger(__name__)

try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class GeminiProvider(AIProvider):
    """
    Production-grade Google Gemini AI provider for JanSetu welfare agent.
    
    Features:
    - Server-side credentials only (GEMINI_API_KEY).
    - Tool declaration mapping via ToolDefinition schemas.
    - Configurable timeouts and exponential backoff retries.
    - Graceful degradation: delegates to a deterministic fallback provider on failure.
    - Deterministic PolicyRuleEngine remains the ultimate eligibility authority.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_retries: int = 2,
        timeout_seconds: float = 20.0,
        fallback: Optional[AIProvider] = None,
    ):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        self.model_name = model or os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
        self.max_retries = max_retries
        self.timeout_seconds = timeout_seconds
        self.fallback = fallback

        if not GEMINI_AVAILABLE:
            if not self.fallback:
                raise RuntimeError("google-genai package is not installed and no fallback provider provided.")
            self.client = None
        elif not self.api_key:
            if not self.fallback:
                raise ValueError("GEMINI_API_KEY is missing and no fallback provider provided.")
            self.client = None
        else:
            self.client = genai.Client(api_key=self.api_key)

    def _convert_tools_to_gemini(self, tools: List[ToolDefinition]) -> Optional[List[Any]]:
        if not GEMINI_AVAILABLE:
            return None

        declarations = []
        for tool in tools:
            schema = tool.input_schema.model_json_schema()
            properties = {}
            for prop_name, prop_info in schema.get("properties", {}).items():
                prop_type = prop_info.get("type", "string").upper()
                if prop_type == "STRING":
                    t = types.Type.STRING
                elif prop_type == "INTEGER":
                    t = types.Type.INTEGER
                elif prop_type == "BOOLEAN":
                    t = types.Type.BOOLEAN
                else:
                    t = types.Type.STRING

                properties[prop_name] = types.Schema(
                    type=t,
                    description=prop_info.get("description", "")
                )

            decl = types.FunctionDeclaration(
                name=tool.name,
                description=tool.description,
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties=properties,
                    required=schema.get("required", [])
                )
            )
            declarations.append(decl)

        if not declarations:
            return None

        return [types.Tool(function_declarations=declarations)]

    async def generate_response(
        self,
        prompt: str,
        context: Dict[str, Any],
        tools: List[ToolDefinition]
    ) -> Dict[str, Any]:
        if not self.client:
            if self.fallback:
                return await self.fallback.generate_response(prompt, context, tools)
            raise RuntimeError("Gemini client not initialized")

        system_instruction = (
            "You are JanSetu Assistant, a sovereign welfare navigator for Indian citizens. "
            "You MUST call provided domain tools to look up profiles, verify documents, "
            "evaluate welfare rules, and prepare applications. "
            "Never invent details, benefits, or policies. "
            "Authoritative eligibility decisions come exclusively from the deterministic Policy Engine."
        )

        gemini_tools = self._convert_tools_to_gemini(tools)
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.2,
            tools=gemini_tools,
        )

        full_prompt = f"Context: {json.dumps(context, default=str)}\n\nCitizen Request: {prompt}"

        last_error = None
        for attempt in range(self.max_retries + 1):
            try:
                response = await asyncio.wait_for(
                    self.client.aio.models.generate_content(
                        model=self.model_name,
                        contents=full_prompt,
                        config=config,
                    ),
                    timeout=self.timeout_seconds,
                )

                if response.function_calls:
                    fc = response.function_calls[0]
                    args = dict(fc.args) if fc.args else {}
                    return {
                        "action": "tool_call",
                        "tool_name": fc.name,
                        "tool_args": args,
                    }

                clean_text = (response.text or "").strip()
                return {
                    "action": "text",
                    "message": clean_text or "Analysis completed successfully.",
                }

            except Exception as e:
                last_error = e
                logger.warning(f"Gemini API attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries:
                    await asyncio.sleep(0.5 * (2 ** attempt))

        logger.error(f"Gemini API failed after {self.max_retries + 1} attempts: {last_error}")
        if self.fallback:
            logger.info("Engaging JanSetu deterministic fallback provider")
            return await self.fallback.generate_response(prompt, context, tools)

        raise RuntimeError(f"Gemini agent failed: {last_error}")

    async def extract_structured_data(
        self,
        text: str,
        schema: Type[BaseModel]
    ) -> BaseModel:
        if not self.client:
            if self.fallback:
                return await self.fallback.extract_structured_data(text, schema)
            raise RuntimeError("Gemini client not initialized")

        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=schema,
            temperature=0.0,
        )

        for attempt in range(self.max_retries + 1):
            try:
                response = await asyncio.wait_for(
                    self.client.aio.models.generate_content(
                        model=self.model_name,
                        contents=f"Extract information into the required schema:\n{text}",
                        config=config,
                    ),
                    timeout=self.timeout_seconds,
                )
                data = json.loads(response.text)
                return schema(**data)
            except Exception as e:
                if attempt < self.max_retries:
                    await asyncio.sleep(0.5 * (2 ** attempt))
                else:
                    if self.fallback:
                        return await self.fallback.extract_structured_data(text, schema)
                    raise ValueError(f"Failed to parse structured data from Gemini: {e}")
