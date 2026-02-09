"""create comments table

Revision ID: 0005_create_comments
Revises: 0004_create_approvals
Create Date: 2025-01-03 00:00:01.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0005_create_comments"
down_revision: Union[str, None] = "0004_create_approvals"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create comments table."""
    op.create_table(
        "comments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("document_id", sa.Integer(), nullable=True),
        sa.Column("approval_id", sa.Integer(), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.ForeignKeyConstraint(["approval_id"], ["approvals.id"]),
    )


def downgrade() -> None:
    """Drop comments table."""
    op.drop_table("comments")
