"""create inventory tables

Revision ID: 0001_create_inventory_tables
Revises: 
Create Date: 2026-02-24 00:00:00
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_create_inventory_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'products',
        sa.Column('sku', sa.String(length=64), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('price', sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('sku'),
    )
    op.create_table(
        'sync_idempotency_records',
        sa.Column('idempotency_key', sa.String(length=128), nullable=False),
        sa.Column('source', sa.String(length=64), nullable=False),
        sa.Column('upserted', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('record_hash', sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint('idempotency_key'),
    )


def downgrade() -> None:
    op.drop_table('sync_idempotency_records')
    op.drop_table('products')
