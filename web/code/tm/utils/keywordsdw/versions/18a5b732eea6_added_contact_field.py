"""added contact field

Revision ID: 18a5b732eea6
Revises: 09dabab336ea
Create Date: 2018-06-28 11:21:15.279055

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '18a5b732eea6'
down_revision = '09dabab336ea'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('scholarship_info', sa.Column('contact', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('scholarship_info', 'contact')
    # ### end Alembic commands ###
