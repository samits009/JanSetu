"""phase_5_scheme_intelligence

Revision ID: 8d4db645b72f
Revises: e8957aeb5353
Create Date: 2026-09-11 21:55:42.001104

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8d4db645b72f'
down_revision: Union[str, Sequence[str], None] = 'e8957aeb5353'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create Enums explicitly in postgres
    op.execute("CREATE TYPE source_type_enum AS ENUM ('HTML', 'PDF', 'JSON', 'API', 'PORTAL', 'FIXTURE')")
    op.execute("CREATE TYPE jurisdiction_level_enum AS ENUM ('CENTRAL', 'STATE', 'DISTRICT', 'LOCAL')")
    op.execute("CREATE TYPE verification_status_enum AS ENUM ('VERIFIED', 'DEMO', 'NEEDS_REVIEW', 'STALE', 'REJECTED', 'UNKNOWN')")
    op.execute("CREATE TYPE portability_state_enum AS ENUM ('PORTABLE', 'NON_PORTABLE', 'CONDITIONALLY_PORTABLE', 'UNKNOWN')")

    # 2. Create tables
    op.create_table('scheme_sources',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('authority', sa.String(), nullable=False),
    sa.Column('source_url', sa.String(), nullable=False),
    sa.Column('source_type', postgresql.ENUM('HTML', 'PDF', 'JSON', 'API', 'PORTAL', 'FIXTURE', name='source_type_enum', create_type=False), nullable=False),
    sa.Column('jurisdiction', postgresql.ENUM('CENTRAL', 'STATE', 'DISTRICT', 'LOCAL', name='jurisdiction_level_enum', create_type=False), nullable=True),
    sa.Column('crawl_frequency', sa.String(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('last_checked', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scheme_sources_id'), 'scheme_sources', ['id'], unique=False)
    
    op.create_table('scheme_versions',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('scheme_id', sa.Uuid(), nullable=False),
    sa.Column('version_number', sa.Integer(), nullable=False),
    sa.Column('effective_from', sa.Date(), nullable=True),
    sa.Column('effective_to', sa.Date(), nullable=True),
    sa.Column('source_id', sa.Uuid(), nullable=True),
    sa.Column('verification_status', postgresql.ENUM('VERIFIED', 'DEMO', 'NEEDS_REVIEW', 'STALE', 'REJECTED', 'UNKNOWN', name='verification_status_enum', create_type=False), nullable=False),
    sa.Column('content_hash', sa.String(), nullable=True),
    sa.Column('published_at', sa.DateTime(), nullable=True),
    sa.Column('requirement_definitions', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['scheme_id'], ['schemes.id'], ),
    sa.ForeignKeyConstraint(['source_id'], ['scheme_sources.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scheme_versions_id'), 'scheme_versions', ['id'], unique=False)
    op.create_index(op.f('ix_scheme_versions_scheme_id'), 'scheme_versions', ['scheme_id'], unique=False)

    # 3. Add current_version_id to schemes
    op.add_column('schemes', sa.Column('current_version_id', sa.Uuid(), nullable=True))

    # 4. Migrate existing schemes to version 1
    op.execute("""
        INSERT INTO scheme_versions (id, scheme_id, version_number, verification_status, requirement_definitions, created_at, updated_at)
        SELECT gen_random_uuid(), id, 1, 'VERIFIED', requirement_definitions, created_at, updated_at FROM schemes;
    """)
    op.execute("""
        UPDATE schemes s
        SET current_version_id = sv.id
        FROM scheme_versions sv
        WHERE sv.scheme_id = s.id;
    """)

    # 5. Rename eligibility_rules to scheme_eligibility_rules and migrate
    op.rename_table('eligibility_rules', 'scheme_eligibility_rules')
    op.execute('ALTER INDEX ix_eligibility_rules_id RENAME TO ix_scheme_eligibility_rules_id')
    op.execute('ALTER INDEX ix_eligibility_rules_scheme_id RENAME TO ix_scheme_eligibility_rules_scheme_id')
    
    op.add_column('scheme_eligibility_rules', sa.Column('version_id', sa.Uuid(), nullable=True))
    op.execute("""
        UPDATE scheme_eligibility_rules r
        SET version_id = sv.id
        FROM scheme_versions sv
        WHERE sv.scheme_id = r.scheme_id;
    """)
    op.alter_column('scheme_eligibility_rules', 'version_id', nullable=False)
    op.create_index(op.f('ix_scheme_eligibility_rules_version_id'), 'scheme_eligibility_rules', ['version_id'], unique=False)
    op.create_foreign_key('fk_scheme_eligibility_rules_version_id', 'scheme_eligibility_rules', 'scheme_versions', ['version_id'], ['id'])
    
    op.add_column('scheme_eligibility_rules', sa.Column('raw_policy_text', sa.String(), nullable=True))
    op.add_column('scheme_eligibility_rules', sa.Column('source_reference', sa.String(), nullable=True))

    # 6. Add references to dependent records
    op.add_column('welfare_applications', sa.Column('scheme_version_id', sa.Uuid(), nullable=True))
    op.create_index(op.f('ix_welfare_applications_scheme_version_id'), 'welfare_applications', ['scheme_version_id'], unique=False)
    op.execute("""
        UPDATE welfare_applications a
        SET scheme_version_id = s.current_version_id
        FROM schemes s
        WHERE a.scheme_id = s.id;
    """)
    op.create_foreign_key('fk_welfare_apps_scheme_version', 'welfare_applications', 'scheme_versions', ['scheme_version_id'], ['id'])

    op.add_column('benefits', sa.Column('scheme_version_id', sa.Uuid(), nullable=True))
    op.create_index(op.f('ix_benefits_scheme_version_id'), 'benefits', ['scheme_version_id'], unique=False)
    op.execute("""
        UPDATE benefits b
        SET scheme_version_id = s.current_version_id
        FROM schemes s
        WHERE b.scheme_id = s.id;
    """)
    op.create_foreign_key('fk_benefits_scheme_version', 'benefits', 'scheme_versions', ['scheme_version_id'], ['id'])

    # 7. Add circular FK to schemes
    op.create_foreign_key('fk_scheme_current_version', 'schemes', 'scheme_versions', ['current_version_id'], ['id'], use_alter=True)

    # 8. Create remaining tables
    op.create_table('scheme_benefits',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('version_id', sa.Uuid(), nullable=False),
    sa.Column('benefit_type', sa.String(), nullable=False),
    sa.Column('amount', sa.Integer(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['version_id'], ['scheme_versions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scheme_benefits_id'), 'scheme_benefits', ['id'], unique=False)
    op.create_index(op.f('ix_scheme_benefits_version_id'), 'scheme_benefits', ['version_id'], unique=False)
    
    op.create_table('scheme_jurisdictions',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('version_id', sa.Uuid(), nullable=False),
    sa.Column('level', postgresql.ENUM('CENTRAL', 'STATE', 'DISTRICT', 'LOCAL', name='jurisdiction_level_enum', create_type=False), nullable=False),
    sa.Column('country', sa.String(), nullable=True),
    sa.Column('state', sa.String(), nullable=True),
    sa.Column('district', sa.String(), nullable=True),
    sa.Column('local_body', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['version_id'], ['scheme_versions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scheme_jurisdictions_id'), 'scheme_jurisdictions', ['id'], unique=False)
    op.create_index(op.f('ix_scheme_jurisdictions_version_id'), 'scheme_jurisdictions', ['version_id'], unique=False)
    
    op.create_table('scheme_portability_rules',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('version_id', sa.Uuid(), nullable=False),
    sa.Column('portability_state', postgresql.ENUM('PORTABLE', 'NON_PORTABLE', 'CONDITIONALLY_PORTABLE', 'UNKNOWN', name='portability_state_enum', create_type=False), nullable=False),
    sa.Column('conditions', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['version_id'], ['scheme_versions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scheme_portability_rules_id'), 'scheme_portability_rules', ['id'], unique=False)
    op.create_index(op.f('ix_scheme_portability_rules_version_id'), 'scheme_portability_rules', ['version_id'], unique=False)
    
    op.create_table('scheme_renewal_rules',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('version_id', sa.Uuid(), nullable=False),
    sa.Column('renewal_required', sa.Boolean(), nullable=True),
    sa.Column('renewal_period_days', sa.Integer(), nullable=True),
    sa.Column('grace_period_days', sa.Integer(), nullable=True),
    sa.Column('deadline_rule', sa.String(), nullable=True),
    sa.Column('required_evidence', sa.JSON(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    sa.ForeignKeyConstraint(['version_id'], ['scheme_versions.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scheme_renewal_rules_id'), 'scheme_renewal_rules', ['id'], unique=False)
    op.create_index(op.f('ix_scheme_renewal_rules_version_id'), 'scheme_renewal_rules', ['version_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'welfare_applications', type_='foreignkey')
    op.drop_index(op.f('ix_welfare_applications_scheme_version_id'), table_name='welfare_applications')
    op.drop_column('welfare_applications', 'scheme_version_id')
    op.drop_constraint('fk_scheme_current_version', 'schemes', type_='foreignkey')
    op.drop_column('schemes', 'current_version_id')
    op.drop_constraint(None, 'benefits', type_='foreignkey')
    op.drop_index(op.f('ix_benefits_scheme_version_id'), table_name='benefits')
    op.drop_column('benefits', 'scheme_version_id')
    op.create_table('eligibility_rules',
    sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('scheme_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('rule_type', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('operator', sa.VARCHAR(), autoincrement=False, nullable=False),
    sa.Column('value', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=False),
    sa.Column('is_mandatory', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=False),
    sa.Column('deleted_at', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['scheme_id'], ['schemes.id'], name=op.f('eligibility_rules_scheme_id_fkey')),
    sa.PrimaryKeyConstraint('id', name=op.f('eligibility_rules_pkey'))
    )
    op.create_index(op.f('ix_eligibility_rules_scheme_id'), 'eligibility_rules', ['scheme_id'], unique=False)
    op.create_index(op.f('ix_eligibility_rules_id'), 'eligibility_rules', ['id'], unique=False)
    op.drop_index(op.f('ix_scheme_renewal_rules_version_id'), table_name='scheme_renewal_rules')
    op.drop_index(op.f('ix_scheme_renewal_rules_id'), table_name='scheme_renewal_rules')
    op.drop_table('scheme_renewal_rules')
    op.drop_index(op.f('ix_scheme_portability_rules_version_id'), table_name='scheme_portability_rules')
    op.drop_index(op.f('ix_scheme_portability_rules_id'), table_name='scheme_portability_rules')
    op.drop_table('scheme_portability_rules')
    op.drop_index(op.f('ix_scheme_jurisdictions_version_id'), table_name='scheme_jurisdictions')
    op.drop_index(op.f('ix_scheme_jurisdictions_id'), table_name='scheme_jurisdictions')
    op.drop_table('scheme_jurisdictions')
    op.drop_index(op.f('ix_scheme_eligibility_rules_version_id'), table_name='scheme_eligibility_rules')
    op.drop_index(op.f('ix_scheme_eligibility_rules_scheme_id'), table_name='scheme_eligibility_rules')
    op.drop_index(op.f('ix_scheme_eligibility_rules_id'), table_name='scheme_eligibility_rules')
    op.drop_table('scheme_eligibility_rules')
    op.drop_index(op.f('ix_scheme_benefits_version_id'), table_name='scheme_benefits')
    op.drop_index(op.f('ix_scheme_benefits_id'), table_name='scheme_benefits')
    op.drop_table('scheme_benefits')
    op.drop_index(op.f('ix_scheme_versions_scheme_id'), table_name='scheme_versions')
    op.drop_index(op.f('ix_scheme_versions_id'), table_name='scheme_versions')
    op.drop_table('scheme_versions')
    op.drop_index(op.f('ix_scheme_sources_id'), table_name='scheme_sources')
    op.drop_table('scheme_sources')
    # ### end Alembic commands ###
