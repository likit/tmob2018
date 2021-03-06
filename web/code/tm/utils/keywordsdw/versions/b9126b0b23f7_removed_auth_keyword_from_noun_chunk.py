"""removed auth-keyword from noun chunk

Revision ID: b9126b0b23f7
Revises: 66dee44a68c8
Create Date: 2018-06-25 00:14:15.288947

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b9126b0b23f7'
down_revision = '66dee44a68c8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('noun_chunks', 'auth_keyword')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('noun_chunks', sa.Column('auth_keyword', sa.BOOLEAN(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
