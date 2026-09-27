import json
from abc import ABC, abstractmethod
from typing import Any, Dict
from app.ingestion.models import SchemeExtractionResult

class BaseExtractor(ABC):
    @abstractmethod
    async def extract(self, clean_content: str) -> SchemeExtractionResult:
        pass

class DeterministicExtractor(BaseExtractor):
    """
    Extracts directly from well-formatted JSON fixtures without AI.
    Used for reliable seeding of our initial dataset.
    """
    async def extract(self, clean_content: str) -> SchemeExtractionResult:
        try:
            data = json.loads(clean_content)
            # Ensure it maps correctly
            return SchemeExtractionResult(**data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Deterministic extractor requires valid JSON content: {e}")

class GeminiExtractor(BaseExtractor):
    """
    Uses Gemini LLM to extract scheme rules from raw policy text.
    (Placeholder for future Phase)
    """
    async def extract(self, clean_content: str) -> SchemeExtractionResult:
        raise NotImplementedError("Gemini extraction not yet fully implemented for ingestion.")
