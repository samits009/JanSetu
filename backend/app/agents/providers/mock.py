from typing import Dict, Any, List, Type, Optional
from pydantic import BaseModel
from .base import AIProvider
from app.agents.tools import ToolDefinition

class MockAIProvider(AIProvider):
    def __init__(self):
        self.state = {}
        
    async def generate_response(
        self, 
        prompt: str, 
        context: Dict[str, Any], 
        tools: List[ToolDefinition]
    ) -> Dict[str, Any]:
        
        # Identify scenario if not set
        if "Delhi se Gorakhpur" in prompt:
            self.state["scenario"] = "loc"
        elif "education assistance" in prompt:
            self.state["scenario"] = "edu"
        elif "Submit karo" in prompt or "Ha, submit karo" in prompt:
            self.state["scenario"] = "sub"
        elif "Additional employment proof required" in prompt or "REQUIRES_EVIDENCE" in prompt:
            self.state["scenario"] = "rec"
        elif "Ha" == prompt.strip() or "Resubmit" in prompt:
            self.state["scenario"] = "resub"

        scenario = self.state.get("scenario")

        import re
        match = re.search(r"['\"]application_id['\"]\s*:\s*['\"]([^'\"]+)['\"]", prompt)
        if match:
            self.state["target_app_id"] = match.group(1)

        # Scenario 1: Location change
        if scenario == "loc":
            step = self.state.get("loc_step", 0)
            if step == 0:
                self.state["loc_step"] = 1
                return {"action": "tool_call", "tool_name": "get_citizen_profile", "tool_args": {}}
            elif step == 1:
                self.state["loc_step"] = 2
                return {"action": "tool_call", "tool_name": "get_welfare_state", "tool_args": {}}
            elif step == 2:
                self.state["loc_step"] = 3
                return {"action": "tool_call", "tool_name": "evaluate_location_change", "tool_args": {"state": "UP", "district": "Gorakhpur"}}
            elif step == 3:
                self.state["loc_step"] = 4
                return {"action": "text", "message": "Maine aapki location UP Gorakhpur update kar di hai. Kuch benefits affect hue hain."}
                
        # Scenario 2: Education Assistance Application
        elif scenario == "edu":
            step = self.state.get("edu_step", 0)
            if step == 0:
                self.state["edu_step"] = 1
                return {"action": "tool_call", "tool_name": "evaluate_eligibility", "tool_args": {"category": "EDUCATION"}}
            elif step == 1:
                self.state["edu_step"] = 2
                return {"action": "tool_call", "tool_name": "search_evidence", "tool_args": {"category": "EDUCATION"}}
            elif step == 2:
                self.state["edu_step"] = 3
                return {"action": "tool_call", "tool_name": "prepare_application", "tool_args": {"scheme_id": self.state.get("target_scheme_id") or context.get("target_scheme_id") or ""}}
            elif step == 3:
                self.state["edu_step"] = 4
                args = {"action": "APPLICATION_SUBMISSION"}
                if self.state.get("target_app_id"):
                    args["application_id"] = self.state.get("target_app_id")
                return {"action": "tool_call", "tool_name": "request_consent", "tool_args": args}
            elif step == 4:
                return {"action": "text", "message": "Kripya consent dijiye."}

        # Scenario 3: Submit application
        elif scenario == "sub":
            step = self.state.get("sub_step", 0)
            if step == 0:
                self.state["sub_step"] = 1
                return {"action": "tool_call", "tool_name": "submit_application", "tool_args": {"application_id": context.get("target_app_id") or self.state.get("target_app_id", "")}}
            elif step == 1:
                return {"action": "text", "message": "Application submit ho gayi hai."}

        # Scenario 4: Recovery
        elif scenario == "rec":
             step = self.state.get("rec_step", 0)
             if step == 0:
                 self.state["rec_step"] = 1
                 return {"action": "tool_call", "tool_name": "interpret_government_response", "tool_args": {"application_id": context.get("target_app_id") or self.state.get("target_app_id", "")}}
             elif step == 1:
                 self.state["rec_step"] = 2
                 return {"action": "tool_call", "tool_name": "search_evidence", "tool_args": {"requirement_type": "EMPLOYMENT"}}
             elif step == 2:
                 self.state["rec_step"] = 3
                 return {"action": "tool_call", "tool_name": "prepare_recovery", "tool_args": {"application_id": context.get("target_app_id") or self.state.get("target_app_id", "")}}
             elif step == 3:
                 self.state["rec_step"] = 4
                 return {"action": "tool_call", "tool_name": "request_consent", "tool_args": {"action": "APPLICATION_RESUBMISSION", "application_id": context.get("target_app_id") or self.state.get("target_app_id", "")}}
             elif step == 4:
                 return {"action": "text", "message": "Kripya nayi evidence submit karne ke liye consent dein."}

        # Resubmit
        elif scenario == "resub":
             step = self.state.get("resub_step", 0)
             if step == 0:
                 self.state["resub_step"] = 1
                 return {"action": "tool_call", "tool_name": "resubmit_application", "tool_args": {"application_id": context.get("target_app_id") or self.state.get("target_app_id", "")}}
             elif step == 1:
                 return {"action": "text", "message": "Application resubmit ho gayi hai."}

        return {"action": "text", "message": "I am a mock provider."}

    async def extract_structured_data(
        self, 
        text: str, 
        schema: Type[BaseModel]
    ) -> BaseModel:
        # Provide some default dummy data matching the schema
        # In a real mock we might use Faker, but here we just try to return a basic instance
        fields = {}
        for name, field_info in schema.model_fields.items():
            if field_info.annotation == str:
                fields[name] = "mock_string"
            elif field_info.annotation == bool:
                fields[name] = True
            elif field_info.annotation == int:
                fields[name] = 1
            else:
                fields[name] = None
        return schema(**fields)
