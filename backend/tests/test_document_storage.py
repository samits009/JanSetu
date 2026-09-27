import pytest
from uuid import uuid4
from app.providers.document_storage import LocalDocumentStorageProvider


@pytest.mark.asyncio
async def test_local_storage_returns_opaque_reference(tmp_path):
    provider = LocalDocumentStorageProvider(str(tmp_path))
    document_id = uuid4()
    reference = await provider.store(document_id, "safe.pdf", b"content")
    assert reference == f"{document_id.hex}/safe.pdf"
    assert (tmp_path / reference).read_bytes() == b"content"
    assert str(tmp_path) not in reference
