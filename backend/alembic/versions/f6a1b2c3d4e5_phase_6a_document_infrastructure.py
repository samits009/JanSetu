"""phase 6a document infrastructure

Revision ID: f6a1b2c3d4e5
Revises: e2356e22d3a5
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "f6a1b2c3d4e5"
down_revision: Union[str, Sequence[str], None] = "e2356e22d3a5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("storage_reference", sa.String(), nullable=True))
    op.add_column("documents", sa.Column("content_hash", sa.String(), nullable=True))
    op.add_column("documents", sa.Column("status", sa.String(), nullable=False, server_default="UPLOADED"))
    op.add_column("documents", sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("documents", sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("documents", sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("documents", sa.Column("metadata", sa.JSON(), nullable=True))
    op.add_column("documents", sa.Column("extraction_method", sa.String(), nullable=True))
    op.create_index("ix_documents_content_hash", "documents", ["content_hash"], unique=False)
    op.add_column("evidence", sa.Column("claim_type", sa.String(), nullable=True))
    op.add_column("evidence", sa.Column("claim_value", sa.JSON(), nullable=True))
    op.add_column("evidence", sa.Column("verification_status", sa.String(), nullable=False, server_default="PENDING"))
    op.execute("UPDATE evidence SET claim_type = evidence_type WHERE claim_type IS NULL")


def downgrade() -> None:
    op.drop_column("evidence", "verification_status")
    op.drop_column("evidence", "claim_value")
    op.drop_column("evidence", "claim_type")
    op.drop_index("ix_documents_content_hash", table_name="documents")
    for column in ("extraction_method", "metadata", "expires_at", "processed_at", "uploaded_at", "status", "content_hash", "storage_reference"):
        op.drop_column("documents", column)