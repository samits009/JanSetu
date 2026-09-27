"""phase 9 production auth identities and verification

Revision ID: a1b2c3d4e5f6
Revises: f1a2b3c4d5e6
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "f1a2b3c4d5e6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Update users table with mobile_number, verification flags, and nullable password_hash
    op.add_column("users", sa.Column("mobile_number", sa.String(), nullable=True))
    op.create_index("ix_users_mobile_number", "users", ["mobile_number"], unique=True)
    op.add_column("users", sa.Column("email_verified", sa.Boolean(), server_default=sa.false(), nullable=False))
    op.add_column("users", sa.Column("mobile_verified", sa.Boolean(), server_default=sa.false(), nullable=False))
    op.alter_column("users", "password_hash", existing_type=sa.String(), nullable=True)

    # 2. Create auth_identities table for multi-provider identities (password, google, etc.)
    op.create_table(
        "auth_identities",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("provider_subject", sa.String(), nullable=False),
        sa.Column("provider_email", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("provider", "provider_subject", name="uq_auth_identities_provider_subject"),
    )
    op.create_index("ix_auth_identities_id", "auth_identities", ["id"])
    op.create_index("ix_auth_identities_user_id", "auth_identities", ["user_id"])
    op.create_index("ix_auth_identities_provider_subject", "auth_identities", ["provider", "provider_subject"])


def downgrade() -> None:
    op.drop_index("ix_auth_identities_provider_subject", table_name="auth_identities")
    op.drop_index("ix_auth_identities_user_id", table_name="auth_identities")
    op.drop_index("ix_auth_identities_id", table_name="auth_identities")
    op.drop_table("auth_identities")

    op.alter_column("users", "password_hash", existing_type=sa.String(), nullable=False)
    op.drop_column("users", "mobile_verified")
    op.drop_column("users", "email_verified")
    op.drop_index("ix_users_mobile_number", table_name="users")
    op.drop_column("users", "mobile_number")
