"""Create bookings table.

Revision ID: 20260907_0001
Revises:
Create Date: 2026-09-07
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260907_0001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "bookings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("phone", sa.String(length=12), nullable=False),
        sa.Column("booking_date", sa.Date(), nullable=False),
        sa.Column("booking_time", sa.Time(), nullable=False),
        sa.Column("guests", sa.SmallInteger(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.CheckConstraint("guests BETWEEN 1 AND 12", name="ck_bookings_guests_range"),
        sa.CheckConstraint("status IN ('active', 'cancelled')", name="ck_bookings_status"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "uq_active_booking_slot",
        "bookings",
        ["booking_date", "booking_time"],
        unique=True,
        sqlite_where=sa.text("status = 'active'"),
    )


def downgrade() -> None:
    op.drop_index("uq_active_booking_slot", table_name="bookings")
    op.drop_table("bookings")
