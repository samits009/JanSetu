from abc import ABC, abstractmethod
from typing import Dict, Any, List, Type, Optional
from pydantic import BaseModel
from app.agents.tools import ToolDefinition

class AIProvider(ABC):
    @abstractmethod
    async def generate_response(
        self, 
        prompt: str, 
        context: Dict[str, Any], 
        tools: List[ToolDefinition]
    ) -> Dict[str, Any]:
        """
        Generate a response or a tool call given the prompt and tools.
        Returns a dictionary which contains either a text response or a tool call.
        {
            "action": "text" | "tool_call",
            "message": "...",
            "tool_name": "...",
            "tool_args": {}
        }
        """
        pass

    @abstractmethod
    async def extract_structured_data(
        self, 
        text: str, 
        schema: Type[BaseModel]
    ) -> BaseModel:
        """
        Extract structured data from text according to a Pydantic schema.
        """
        pass
