"""changed the type of the pub start and end fields

Revision ID: 30b31d2baf01
Revises: 34d15f0fb644
Create Date: 2019-12-30 02:54:28.587915

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '30b31d2baf01'
down_revision = '34d15f0fb644'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('dim_scopus_author_detail', 'pub_start')
    op.drop_column('dim_scopus_author_detail', 'pub_end')
    op.add_column('dim_scopus_author_detail', sa.Column('pub_start', sa.Integer()))
    op.add_column('dim_scopus_author_detail', sa.Column('pub_end', sa.Integer()))


def downgrade():
    op.drop_column('dim_scopus_author_detail', 'pub_start')
    op.drop_column('dim_scopus_author_detail', 'pub_end')
    op.add_column('dim_scopus_author_detail', sa.Column('pub_start', sa.Date()))
    op.add_column('dim_scopus_author_detail', sa.Column('pub_end', sa.Date()))
