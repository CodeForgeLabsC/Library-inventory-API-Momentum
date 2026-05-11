"""create books table

Revision ID: 20260510_0001
Revises:
Create Date: 2026-05-10 14:35:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260510_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "books",
        sa.Column("serial_number", sa.String(length=6), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("author", sa.String(length=255), nullable=False),
        sa.Column("is_borrowed", sa.Boolean(), nullable=False),
        sa.Column("borrowed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("borrower_card_number", sa.String(length=6), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("serial_number"),
    )
    op.create_index(
        op.f("ix_books_serial_number"), "books", ["serial_number"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_books_serial_number"), table_name="books")
    op.drop_table("books")
