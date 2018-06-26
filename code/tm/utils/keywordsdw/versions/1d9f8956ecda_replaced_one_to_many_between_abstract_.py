"""replaced one-to-many between abstract and keywords to many-to-many

Revision ID: 1d9f8956ecda
Revises: b9e7bb848b35
Create Date: 2018-06-24 22:52:22.824630

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1d9f8956ecda'
down_revision = 'b9e7bb848b35'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('abstract_has_keywords',
    sa.Column('abstract_id', sa.Integer(), nullable=True),
    sa.Column('keyword_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['abstract_id'], ['abstracts.id'], ),
    sa.ForeignKeyConstraint(['keyword_id'], ['keywords.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('abstract_has_keywords')
    # ### end Alembic commands ###