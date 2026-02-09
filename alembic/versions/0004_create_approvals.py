"""create approvals tables

Revision ID: 0004_create_approvals
Revises: 0003_create_documents
Create Date: 2025-01-03 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0004_create_approvals"
down_revision: Union[str, None] = "0003_create_documents"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create approvals tables."""
    op.create_table(
        "approvals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
    )
    op.create_table(
        "approval_steps",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("approval_id", sa.Integer(), nullable=False),
        sa.Column("approver_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["approval_id"], ["approvals.id"]),
        sa.ForeignKeyConstraint(["approver_id"], ["users.id"]),
    )


def downgrade() -> None:
    """Drop approvals tables."""
    op.drop_table("approval_steps")
    op.drop_table("approvals")
