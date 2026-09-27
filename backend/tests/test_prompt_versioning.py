from app.providers.document_processing import GeminiDocumentProcessingProvider


def test_prompt_version_is_explicit():
    assert GeminiDocumentProcessingProvider.PROMPT_VERSION == "document_extraction_v1"
