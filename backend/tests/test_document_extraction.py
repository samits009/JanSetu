from app.ingestion.document_extraction import DocumentClaim, DocumentExtraction


def test_document_extraction_claim_contract():
    extraction = DocumentExtraction(claims=[DocumentClaim(
        field="name", value="Ramesh Kumar", confidence="HIGH",
        source_location="page:1", extraction_method="MOCK"
    )], extraction_method="MOCK")
    assert extraction.claims[0].field == "name"
    assert extraction.claims[0].source_location == "page:1"
