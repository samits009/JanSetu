import pytest
from app.ingestion.extractor import DeterministicExtractor
from app.domain.enums import SourceType

@pytest.mark.asyncio
async def test_provenance_extraction():
    extractor = DeterministicExtractor()
    json_fixture = """
    {
      "official_name": "UP BOCW",
      "category": "EMPLOYMENT",
      "description": "Mock description",
      "source_type": "FIXTURE",
      "source_reference": "UP-BOCW-2026",
      "authority": "UP Labour Department",
      "retrieved_at": "2026-09-11T12:00:00Z"
    }
    """
    
    extracted = await extractor.extract(json_fixture)
    
    assert extracted.source_type == SourceType.FIXTURE
    assert extracted.source_reference == "UP-BOCW-2026"
    assert extracted.authority == "UP Labour Department"
    assert extracted.retrieved_at == "2026-09-11T12:00:00Z"
