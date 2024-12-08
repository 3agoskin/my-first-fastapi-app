"""add unit_price  column to order product association table

Revision ID: 813c829d71b9
Revises: 822d5cd0ba6d
Create Date: 2024-12-08 12:14:46.208165

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "813c829d71b9"
down_revision: Union[str, None] = "822d5cd0ba6d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "order_product_association",
        sa.Column("unit_price", sa.Integer(), server_default="0", nullable=False),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("order_product_association", "unit_price")
    # ### end Alembic commands ###
