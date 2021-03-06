"""added end date field and changed the author ID field to the identifier field

Revision ID: a6b8e1c2db9f
Revises: de5332e18490
Create Date: 2019-12-30 03:25:54.264272

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a6b8e1c2db9f'
down_revision = 'de5332e18490'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('dim_scopus_author_detail', sa.Column('end_date', sa.Date(), nullable=True))
    op.add_column('dim_scopus_author_detail', sa.Column('identifier', sa.String(), nullable=True))
    op.drop_column('dim_scopus_author_detail', 'author_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('dim_scopus_author_detail', sa.Column('author_id', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('dim_scopus_author_detail', 'identifier')
    op.drop_column('dim_scopus_author_detail', 'end_date')
    # ### end Alembic commands ###
