import pytest
import os
from unittest.mock import patch, MagicMock
from app.agents.providers.gemini import GeminiProvider, GEMINI_AVAILABLE
from app.agents.tools import tool_registry

def test_gemini_provider_init_no_key():
    with patch.dict(os.environ, {}, clear=True):
        if GEMINI_AVAILABLE:
            with pytest.raises(ValueError, match="GEMINI_API_KEY is missing."):
                GeminiProvider()

def test_gemini_provider_init_with_key():
    with patch.dict(os.environ, {"GEMINI_API_KEY": "dummy_key"}):
        if GEMINI_AVAILABLE:
            provider = GeminiProvider()
            assert provider.api_key == "dummy_key"

@pytest.mark.asyncio
async def test_gemini_provider_convert_tools():
    if not GEMINI_AVAILABLE:
        pytest.skip("google-genai not available")
        
    with patch.dict(os.environ, {"GEMINI_API_KEY": "dummy"}):
        provider = GeminiProvider()
        tools = tool_registry.get_all_tools()
        
        # Test conversion
        gemini_tools = provider._convert_tools_to_gemini(tools[:2])
        assert gemini_tools is not None
        assert len(gemini_tools) == 1 # Returns a list with one Tool object containing multiple declarations
        assert len(gemini_tools[0].function_declarations) == 2
