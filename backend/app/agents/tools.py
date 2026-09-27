from typing import Callable, Dict, Any, Type, Optional, List
from pydantic import BaseModel
from .permissions import ToolPermissionLevel
from .tool_schemas import ToolResult

class ToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: Type[BaseModel]
    permission_level: ToolPermissionLevel
    requires_consent: bool = False
    audit_action: Optional[str] = None
    func: Callable

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}

    def register(
        self,
        name: str,
        description: str,
        input_schema: Type[BaseModel],
        permission_level: ToolPermissionLevel,
        requires_consent: bool = False,
        audit_action: Optional[str] = None
    ):
        def decorator(func: Callable):
            self._tools[name] = ToolDefinition(
                name=name,
                description=description,
                input_schema=input_schema,
                permission_level=permission_level,
                requires_consent=requires_consent,
                audit_action=audit_action,
                func=func
            )
            return func
        return decorator

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)
    
    def get_all_tools(self) -> List[ToolDefinition]:
        return list(self._tools.values())

tool_registry = ToolRegistry()
