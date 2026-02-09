"""create document metrics table

Revision ID: 0006_create_document_metrics
Revises: 0005_create_comments
Create Date: 2025-01-03 00:00:02.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0006_create_document_metrics"
down_revision: Union[str, None] = "0005_create_comments"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create document metrics table."""
    op.create_table(
        "document_metrics",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("value", sa.String(length=255), nullable=False),
        sa.Column("unit", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
    )


def downgrade() -> None:
    """Drop document metrics table."""
    op.drop_table("document_metrics")
