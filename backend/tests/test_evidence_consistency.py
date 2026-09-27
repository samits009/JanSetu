import pytest
from app.models.evidence import Evidence
from app.services.evidence_consistency import EvidenceConsistencyService, ConsistencyResult


@pytest.mark.asyncio
async def test_conflicting_claims_need_review():
    items = [
        Evidence(evidence_type="IDENTITY", claim_type="name", claim_value={"value": "Ramesh Kumar"}, data={"name": "Ramesh Kumar"}),
        Evidence(evidence_type="IDENTITY", claim_type="name", claim_value={"value": "Ramesh Kumar Singh"}, data={"name": "Ramesh Kumar Singh"}),
    ]
    result = await EvidenceConsistencyService().check(items)
    assert result["status"] == ConsistencyResult.CONFLICT


@pytest.mark.asyncio
async def test_consistent_claims_are_consistent():
    item = Evidence(evidence_type="IDENTITY", claim_type="name", claim_value={"value": "Ramesh Kumar"}, data={"name": "Ramesh Kumar"})
    result = await EvidenceConsistencyService().check([item])
    assert result["status"] == ConsistencyResult.CONSISTENT
