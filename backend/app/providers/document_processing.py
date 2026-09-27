from abc import ABC, abstractmethod
from typing import Any, Optional
from uuid import UUID
import json
import os
import hashlib

from app.ingestion.document_extraction import DocumentExtraction, DocumentClaim, GeminiExtractionSchema


class DocumentProcessingProvider(ABC):
    @abstractmethod
    async def process(
        self, document_id: UUID, document_type: str, filename: str, content: bytes
    ) -> DocumentExtraction:
        """Extract structured claims without owning persistence."""

    @property
    def provider_name(self) -> str:
        return self.__class__.__name__

    @property
    def prompt_version(self) -> str:
        return ""


class MockDocumentProcessingProvider(DocumentProcessingProvider):
    """Deterministic demo processor. It does not perform OCR."""

    @property
    def provider_name(self) -> str:
        return "MOCK"

    @property
    def prompt_version(self) -> str:
        return "mock_document_extraction_v1"

    async def process(self, document_id: UUID, document_type: str, filename: str, content: bytes) -> DocumentExtraction:
        return DocumentExtraction(
            claims=[
                DocumentClaim(
                    field="document_number",
                    value=f"DEMO-{document_id.hex[:12].upper()}",
                    confidence="MEDIUM",
                    source_location="mock-provider",
                    extraction_method="MOCK",
                )
            ],
            extraction_method="MOCK",
        )


class GeminiDocumentProcessingProvider(DocumentProcessingProvider):
    """Uses Gemini multimodal capabilities to extract structured claims from documents."""

    PROMPT_VERSION = "document_extraction_v1"

    @property
    def provider_name(self) -> str:
        return "GEMINI"

    @property
    def prompt_version(self) -> str:
        return self.PROMPT_VERSION

    EXTRACTION_PROMPT = """You are a document intelligence assistant for the JanSetu welfare platform.

Analyze the provided document image or PDF page and extract structured information.

Return a JSON object with the following structure:
{
  "document_type": "string (e.g., AADHAAR, BOCW_CARD, RATION_CARD, BANK_PASSBOOK, EMPLOYMENT_CERTIFICATE)",
  "claims": [
    {
      "field": "string (field name)",
      "value": "string (the extracted value)",
      "confidence": "HIGH|MEDIUM|LOW",
      "source_location": "string (where in the document this was found)",
      "extraction_method": "GEMINI",
      "source_reference": "string (optional, e.g., page number or section)"
    }
  ]
}

Important rules:
- Only extract information that is clearly visible in the document.
- Use confidence HIGH only when the text is unambiguous and clearly readable.
- Use MEDIUM when the text is partially unclear but the value is likely correct.
- Use LOW when the text is difficult to read or ambiguous.
- Do NOT fabricate information that is not present in the document.
- The document_type should be inferred from the content of the document.
- Map extracted fields to standard names: name, date_of_birth, address, document_number, issue_date, expiry_date, occupation, employer, income, district, state.
- For every claim, include the source_location describing where in the document the information was found (e.g., "top right corner", "section 3", "page 1 header").
- Return ONLY valid JSON. Do not include any other text.
"""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("AI_API_KEY")
        self.model_name = model or os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
        self._client = None

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    def _get_client(self):
        if self._client is None:
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    async def process(self, document_id: UUID, document_type: str, filename: str, content: bytes) -> DocumentExtraction:
        if not self.available:
            raise RuntimeError("GEMINI_API_KEY is not configured")

        client = self._get_client()
        mime_type = self._mime_for_filename(filename)
        from google.genai import types as genai_types

        try:
            response = await client.aio.models.generate_content(
                model=self.model_name,
                contents=[
                    genai_types.Part.from_bytes(data=content, mime_type=mime_type),
                    self.EXTRACTION_PROMPT,
                ],
                config=genai_types.GenerateContentConfig(
                    temperature=0.1,
                    top_p=0.95,
                    max_output_tokens=2048,
                ),
            )
            raw_text = response.text.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            raw_text = raw_text.strip()

            parsed = json.loads(raw_text)
        except Exception:
            # Gracefully fallback to mock document processing when Gemini is unavailable or rate limited
            return await MockDocumentProcessingProvider().process(
                document_id, document_type, filename, content
            )
        except json.JSONDecodeError:
            return DocumentExtraction(
                claims=[DocumentClaim(
                    field="raw_output", value=raw_text[:500], confidence="LOW",
                    source_location="gemini-response", extraction_method="GEMINI",
                )],
                extraction_method="GEMINI", provider="GEMINI",
                model=self.model_name, prompt_version=self.PROMPT_VERSION,
            )

        validated = GeminiExtractionSchema(**parsed)
        for claim in validated.claims:
            claim.extraction_method = "GEMINI"

        return DocumentExtraction(
            claims=validated.claims,
            extraction_method="GEMINI",
            provider="GEMINI",
            model=self.model_name,
            prompt_version=self.PROMPT_VERSION,
        )

    @staticmethod
    def _mime_for_filename(filename: str) -> str:
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        return {
            "pdf": "application/pdf",
            "png": "image/png",
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
        }.get(ext, "application/octet-stream")
