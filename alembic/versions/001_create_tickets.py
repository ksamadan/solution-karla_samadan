"""Create tickets table

Revision ID: 001_create_tickets
Revises:
Create Date: 2026-01-01
"""

from alembic import op
import sqlalchemy as sa

revision = "001_create_tickets"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        "tickets",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=False),
        sa.Column("assignee", sa.String(length=100), nullable=True),
        sa.Column("source_json", sa.JSON(), nullable=True),
    )

    op.create_index("ix_tickets_id", "tickets", ["id"])
    op.create_index("ix_tickets_title", "tickets", ["title"])
    op.create_index("ix_tickets_status", "tickets", ["status"])
    op.create_index("ix_tickets_priority", "tickets", ["priority"])
    op.create_index("ix_tickets_assignee", "tickets", ["assignee"])

def downgrade() -> None:
    op.drop_index("ix_tickets_assignee", table_name="tickets")
    op.drop_index("ix_tickets_priority", table_name="tickets")
    op.drop_index("ix_tickets_status", table_name="tickets")
    op.drop_index("ix_tickets_title", table_name="tickets")
    op.drop_index("ix_tickets_id", table_name="tickets")

    op.drop_table("tickets")
