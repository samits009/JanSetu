"""phase 7 document intelligence metadata

Revision ID: b7c8d9e0f1a2
Revises: a6b7c8d9e0f1
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "b7c8d9e0f1a2"
down_revision: Union[str, Sequence[str], None] = "a6b7c8d9e0f1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("processing_provider", sa.String(), nullable=True))
    op.add_column("documents", sa.Column("processing_model", sa.String(), nullable=True))
    op.add_column("documents", sa.Column("prompt_version", sa.String(), nullable=True))
    op.add_column("evidence", sa.Column("provenance", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("evidence", "provenance")
    op.drop_column("documents", "prompt_version")
    op.drop_column("documents", "processing_model")
    op.drop_column("documents", "processing_provider")