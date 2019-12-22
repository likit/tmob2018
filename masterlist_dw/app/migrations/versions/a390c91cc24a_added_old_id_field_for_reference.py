"""added old Id field for reference

Revision ID: a390c91cc24a
Revises: d62f0f442a36
Create Date: 2019-12-22 23:05:12.997470

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a390c91cc24a'
down_revision = 'd62f0f442a36'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('fact_researchers', sa.Column('old_id', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('fact_researchers', 'old_id')
    # ### end Alembic commands ###
