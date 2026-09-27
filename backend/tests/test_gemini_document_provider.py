import json
import pytest
from uuid import uuid4
from app.providers.document_processing import GeminiDocumentProcessingProvider


class FakeResponse:
    text = json.dumps({
        "document_type": "BOCW_CARD",
        "claims": [{
            "field": "name", "value": "Ramesh Kumar", "confidence": "HIGH",
            "source_location": "page 1 header", "extraction_method": "GEMINI",
            "source_reference": "page:1",
        }],
    })


class FakeModels:
    async def generate_content(self, **kwargs):
        return FakeResponse()


class FakeAio:
    models = FakeModels()


class FakeClient:
    aio = FakeAio()


@pytest.mark.asyncio
async def test_gemini_provider_validates_structured_output(monkeypatch):
    provider = GeminiDocumentProcessingProvider(api_key="test-key", model="test-model")
    provider._client = FakeClient()
    result = await provider.process(uuid4(), "BOCW_CARD", "worker.pdf", b"pdf")
    assert result.provider == "GEMINI"
    assert result.model == "test-model"
    assert result.prompt_version == "document_extraction_v1"
    assert result.claims[0].confidence == "HIGH"


def test_gemini_provider_requires_key():
    provider = GeminiDocumentProcessingProvider(api_key=None)
    assert provider.available is False
