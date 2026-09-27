from enum import StrEnum
from typing import Any, Dict, List
from app.models.evidence import Evidence


class ConsistencyResult(StrEnum):
    CONSISTENT = "CONSISTENT"
    CONFLICT = "CONFLICT"
    INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


class EvidenceConsistencyService:
    """Detects contradictions without deciding eligibility or rejecting citizens."""

    async def check(self, evidence: List[Evidence]) -> Dict[str, Any]:
        grouped: Dict[str, List[Any]] = {}
        for item in evidence:
            value = item.claim_value or item.data
            if isinstance(value, dict) and "value" in value:
                value = value["value"]
            if value is not None:
                grouped.setdefault(item.claim_type or item.evidence_type, []).append(value)

        conflicts = []
        for claim_type, values in grouped.items():
            normalized = {str(value).strip().casefold() for value in values}
            if len(normalized) > 1:
                conflicts.append({"claim_type": claim_type, "values": values})

        if conflicts:
            return {"status": ConsistencyResult.CONFLICT.value, "conflicts": conflicts}
        if not grouped:
            return {"status": ConsistencyResult.INSUFFICIENT_DATA.value, "conflicts": []}
        return {"status": ConsistencyResult.CONSISTENT.value, "conflicts": []}
