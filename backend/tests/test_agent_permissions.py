import pytest
from app.agents.tools import tool_registry
from app.agents.permissions import ToolPermissionLevel

def test_tool_registry_has_tools():
    tools = tool_registry.get_all_tools()
    assert len(tools) >= 10

def test_tool_schema_and_permissions():
    tools = tool_registry.get_all_tools()
    for tool in tools:
        assert tool.name
        assert tool.description
        assert tool.input_schema
        assert isinstance(tool.permission_level, ToolPermissionLevel)
        
        if tool.permission_level == ToolPermissionLevel.HIGH_IMPACT:
            # High impact tools MUST have requires_consent = True according to our rules
            if tool.name not in ["request_consent"]: # request_consent is HIGH_IMPACT but doesn't require consent to *call* it
                assert tool.requires_consent is True
        elif tool.permission_level == ToolPermissionLevel.READ_ONLY:
            assert tool.requires_consent is False

def test_tool_get():
    tool = tool_registry.get_tool("get_citizen_profile")
    assert tool is not None
    assert tool.permission_level == ToolPermissionLevel.READ_ONLY
