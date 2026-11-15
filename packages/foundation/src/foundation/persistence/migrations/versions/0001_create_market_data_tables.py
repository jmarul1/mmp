"""create market data tables

Revision ID: 0001
Revises:
Create Date: 2026-11-15 13:17:24.877363
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "options",
        sa.Column("snapshot_date", sa.Date(), nullable=False),
        sa.Column("contract_symbol", sa.String(), nullable=False),
        sa.Column("symbol", sa.String(), nullable=False),
        sa.Column("side", sa.String(), nullable=False),
        sa.Column("expiration", sa.Date(), nullable=False),
        sa.Column("strike", sa.Double(), nullable=False),
        sa.Column("last_trade_date", sa.DateTime(), nullable=True),
        sa.Column("last_price", sa.Double(), nullable=True),
        sa.Column("bid", sa.Double(), nullable=True),
        sa.Column("ask", sa.Double(), nullable=True),
        sa.Column("change", sa.Double(), nullable=True),
        sa.Column("percent_change", sa.Double(), nullable=True),
        sa.Column("volume", sa.Double(), nullable=True),
        sa.Column("open_interest", sa.Double(), nullable=True),
        sa.Column("implied_volatility", sa.Double(), nullable=True),
        sa.Column("in_the_money", sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint("snapshot_date", "contract_symbol"),
    )
    with op.batch_alter_table("options", schema=None) as batch_op:
        batch_op.create_index(
            "options_symbol", ["symbol", "snapshot_date"], unique=False
        )

    op.create_table(
        "prices",
        sa.Column("symbol", sa.String(), nullable=False),
        sa.Column("ts", sa.DateTime(), nullable=False),
        sa.Column("open", sa.Double(), nullable=True),
        sa.Column("high", sa.Double(), nullable=True),
        sa.Column("low", sa.Double(), nullable=True),
        sa.Column("close", sa.Double(), nullable=True),
        sa.Column("volume", sa.Double(), nullable=True),
        sa.Column("dividends", sa.Double(), nullable=True),
        sa.Column("stock_splits", sa.Double(), nullable=True),
        sa.PrimaryKeyConstraint("symbol", "ts"),
    )
    op.create_table(
        "ratings",
        sa.Column("snapshot_date", sa.Date(), nullable=False),
        sa.Column("symbol", sa.String(), nullable=False),
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("published", sa.Date(), nullable=False),
        sa.Column("buy", sa.Double(), nullable=True),
        sa.Column("hold", sa.Double(), nullable=True),
        sa.Column("sell", sa.Double(), nullable=True),
        sa.PrimaryKeyConstraint("snapshot_date", "symbol", "source", "published"),
    )


def downgrade() -> None:
    op.drop_table("ratings")
    op.drop_table("prices")
    with op.batch_alter_table("options", schema=None) as batch_op:
        batch_op.drop_index("options_symbol")

    op.drop_table("options")
