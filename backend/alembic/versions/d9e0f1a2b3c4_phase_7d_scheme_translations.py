"""phase 7d scheme translations

Revision ID: d9e0f1a2b3c4
Revises: c8d9e0f1a2b3
Create Date: 2026-09-26 19:47:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = 'd9e0f1a2b3c4'
down_revision = 'c8d9e0f1a2b3'
branch_labels = None
depends_on = None


def upgrade():
    # 1. scheme_translations
    op.create_table(
        'scheme_translations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('scheme_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('schemes.id', ondelete='CASCADE'), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=False),
        sa.Column('official_name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('benefit_description', sa.String(), nullable=True),
        sa.Column('source_language', sa.String(length=10), nullable=False, server_default='en'),
        sa.Column('is_authoritative', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_scheme_translations_scheme_id', 'scheme_translations', ['scheme_id'])
    op.create_index('ix_scheme_translations_language', 'scheme_translations', ['language'])

    # 2. requirement_translations
    op.create_table(
        'requirement_translations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('requirement_name', sa.String(), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=False),
        sa.Column('label', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_requirement_translations_req_name', 'requirement_translations', ['requirement_name'])
    op.create_index('ix_requirement_translations_language', 'requirement_translations', ['language'])


def downgrade():
    op.drop_table('requirement_translations')
    op.drop_table('scheme_translations')
