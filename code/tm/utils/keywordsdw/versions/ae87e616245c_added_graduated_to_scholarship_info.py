"""added graduated to scholarship info

Revision ID: ae87e616245c
Revises: 8eeb833af62b
Create Date: 2019-04-25 09:27:51.904965

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ae87e616245c'
down_revision = '8eeb833af62b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('scholarship_info', sa.Column('graduated_date', sa.Date(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('scholarship_info', 'graduated_date')
    # ### end Alembic commands ###
