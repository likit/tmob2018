"""added scopus fields dimension table

Revision ID: 1ed63a372ad3
Revises: 722bce41fec9
Create Date: 2019-12-29 08:51:23.533297

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1ed63a372ad3'
down_revision = '722bce41fec9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('scopus_fields',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('code', sa.Integer(), nullable=True),
    sa.Column('abbrev', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('detail', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('code')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('scopus_fields')
    # ### end Alembic commands ###
