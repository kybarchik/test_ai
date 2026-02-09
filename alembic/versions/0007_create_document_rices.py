"""create document rices table

Revision ID: 0007_create_document_rices
Revises: 0006_create_document_metrics
Create Date: 2025-01-03 00:00:03.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0007_create_document_rices"
down_revision: Union[str, None] = "0006_create_document_metrics"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create document rices table."""
    op.create_table(
        "document_rices",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("reach", sa.Float(), nullable=False),
        sa.Column("impact", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("effort", sa.Float(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"]),
    )


def downgrade() -> None:
    """Drop document rices table."""
    op.drop_table("document_rices")
