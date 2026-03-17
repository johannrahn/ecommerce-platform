"""add coupon description, max_discount_amount, and cart coupon_code

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-03-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add description and max_discount_amount to coupons
    op.add_column('coupons', sa.Column('description', sa.String(length=500), nullable=True))
    op.add_column('coupons', sa.Column('max_discount_amount', sa.Numeric(precision=10, scale=2), nullable=True))

    # Add coupon_code to carts
    op.add_column('carts', sa.Column('coupon_code', sa.String(length=50), nullable=True))


def downgrade() -> None:
    op.drop_column('carts', 'coupon_code')
    op.drop_column('coupons', 'max_discount_amount')
    op.drop_column('coupons', 'description')
