"""added field city to affiliation model

Revision ID: 852e43032458
Revises: 9b3e562ca76e
Create Date: 2018-06-24 19:59:03.628540

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '852e43032458'
down_revision = '9b3e562ca76e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('affils', sa.Column('city', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('affils', 'city')
    # ### end Alembic commands ###
