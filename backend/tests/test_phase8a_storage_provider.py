import pytest
import uuid
import os
from app.providers.document_storage import (
    LocalDocumentStorageProvider,
    CloudDocumentStorageProvider,
    get_document_storage_provider,
)


@pytest.mark.asyncio
async def test_local_document_storage_provider(tmp_path):
    provider = LocalDocumentStorageProvider(root=str(tmp_path))
    doc_id = uuid.uuid4()
    content = b"%PDF-1.4 test local document content"
    filename = "test_id.pdf"

    # Store
    ref = await provider.store(doc_id, filename, content)
    assert doc_id.hex in ref
    assert filename in ref

    # Retrieve
    retrieved = await provider.retrieve(ref)
    assert retrieved == content

    # Delete
    await provider.delete(ref)
    with pytest.raises(FileNotFoundError):
        await provider.retrieve(ref)


@pytest.mark.asyncio
async def test_local_provider_path_traversal_protection(tmp_path):
    provider = LocalDocumentStorageProvider(root=str(tmp_path))
    with pytest.raises(ValueError, match="Invalid storage reference"):
        await provider.retrieve("../../secret.txt")


@pytest.mark.asyncio
async def test_cloud_document_storage_provider_abstraction():
    provider = CloudDocumentStorageProvider(
        bucket_name="jansetu-sovereign-vault",
        prefix="verified_docs",
        region="ap-south-1"
    )
    doc_id = uuid.uuid4()
    content = b"%PDF-1.4 test cloud byte content"
    filename = "salary_slip.pdf"

    # Store in cloud abstraction
    storage_ref = await provider.store(doc_id, filename, content)
    assert storage_ref.startswith("cloud://jansetu-sovereign-vault/verified_docs/")
    assert doc_id.hex in storage_ref
    assert filename in storage_ref

    # Retrieve from cloud abstraction
    retrieved = await provider.retrieve(storage_ref)
    assert retrieved == content

    # Delete
    await provider.delete(storage_ref)
    with pytest.raises(FileNotFoundError):
        await provider.retrieve(storage_ref)


def test_get_document_storage_provider_factory(monkeypatch, tmp_path):
    # Default is local
    monkeypatch.delenv("DOCUMENT_STORAGE_PROVIDER", raising=False)
    provider_default = get_document_storage_provider()
    assert isinstance(provider_default, LocalDocumentStorageProvider)

    # Cloud setting
    monkeypatch.setenv("DOCUMENT_STORAGE_PROVIDER", "cloud")
    provider_cloud = get_document_storage_provider()
    assert isinstance(provider_cloud, CloudDocumentStorageProvider)

    # S3 setting
    monkeypatch.setenv("DOCUMENT_STORAGE_PROVIDER", "s3")
    provider_s3 = get_document_storage_provider()
    assert isinstance(provider_s3, CloudDocumentStorageProvider)

    # Reset
    monkeypatch.setenv("DOCUMENT_STORAGE_PROVIDER", "local")
    provider_local = get_document_storage_provider()
    assert isinstance(provider_local, LocalDocumentStorageProvider)
