import pytest
import uuid
from typing import List, Dict, Any
from app.agents.providers.mock import MockAIProvider
from app.agents.welfare_agent import WelfareAgent
from app.agents.tools import ToolDefinition

class FailingProvider(MockAIProvider):
    async def generate_response(
        self, 
        prompt: str, 
        context: Dict[str, Any], 
        tools: List[ToolDefinition]
    ) -> Dict[str, Any]:
        # Always return the same tool call to trigger the loop protection
        return {"action": "tool_call", "tool_name": "get_citizen_profile", "tool_args": {}}

@pytest.mark.asyncio
async def test_agent_loop_protection():
    provider = FailingProvider()
    agent = WelfareAgent(provider)
    agent.max_repeated_calls = 2
    
    # Mock context
    class DummyContext:
        citizen_id = uuid.uuid4()
        cit_repo = None
    
    # In reality get_citizen_profile will fail because repo is None, 
    # but the failing result is fed back and FailingProvider still returns the same tool call.
    response = await agent.chat("trigger loop", DummyContext())
    
    assert response.workflow_state == "FAILED"
    assert response.message == "Agent could not safely complete the workflow."
    assert "get_citizen_profile" in response.actions
    assert len(response.execution_trace) == 2
