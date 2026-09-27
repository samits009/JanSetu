"""phase_5b_scheme_audit_events

Revision ID: e2356e22d3a5
Revises: 8d4db645b72f
Create Date: 2026-09-11 23:30:19.625850

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e2356e22d3a5'
down_revision: Union[str, Sequence[str], None] = '8d4db645b72f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create scheme_audit_events table for Scheme Intelligence audit trail."""
    op.create_table(
        'scheme_audit_events',
        sa.Column('id', sa.dialects.postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('actor', sa.String(), nullable=False),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('scheme_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('schemes.id'), nullable=True),
        sa.Column('version_id', sa.dialects.postgresql.UUID(as_uuid=True), sa.ForeignKey('scheme_versions.id'), nullable=True),
        sa.Column('result', sa.String(), nullable=True),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.Column('occurred_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    """Drop scheme_audit_events table."""
    op.drop_table('scheme_audit_events')
