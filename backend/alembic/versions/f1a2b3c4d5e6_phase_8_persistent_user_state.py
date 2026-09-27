from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision = 'f1a2b3c4d5e6'
down_revision = 'd9e0f1a2b3c4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('citizens', sa.Column('gender', sa.String(), nullable=True))
    op.add_column('citizens', sa.Column('onboarding_completed', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('citizens', sa.Column('onboarding_step', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('employments', sa.Column('employment_status', sa.String(), nullable=True))
    op.add_column('employments', sa.Column('annual_income', sa.Integer(), nullable=True))
    op.add_column('households', sa.Column('member_count', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('households', sa.Column('dependents_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('households', sa.Column('children_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('account_status', sa.String(), nullable=False, server_default='ACTIVE'))
    op.add_column('users', sa.Column('last_login', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'last_login')
    op.drop_column('users', 'account_status')
    op.drop_column('households', 'children_count')
    op.drop_column('households', 'dependents_count')
    op.drop_column('households', 'member_count')
    op.drop_column('employments', 'annual_income')
    op.drop_column('employments', 'employment_status')
    op.drop_column('citizens', 'onboarding_step')
    op.drop_column('citizens', 'onboarding_completed')
    op.drop_column('citizens', 'gender')
