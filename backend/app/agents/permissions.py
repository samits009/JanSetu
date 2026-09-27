from enum import Enum

class ToolPermissionLevel(Enum):
    READ_ONLY = "READ_ONLY"
    LOW_IMPACT = "LOW_IMPACT"
    HIGH_IMPACT = "HIGH_IMPACT"
