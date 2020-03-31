"""refactored the keywords and nounchunks tables using more denormalized form instead of association tables

Revision ID: e3731a81fcaa
Revises: 9e5a55e7582b
Create Date: 2018-10-07 20:12:13.198598

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e3731a81fcaa'
down_revision = '9e5a55e7582b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('keyword_lists',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('keyword_id', sa.Integer(), nullable=True),
    sa.Column('field_pub_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['field_pub_id'], ['field_pubs.id'], ),
    sa.ForeignKeyConstraint(['keyword_id'], ['keywords.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('noun_chunk_lists',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('noun_chunk_id', sa.Integer(), nullable=True),
    sa.Column('field_pub_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['field_pub_id'], ['field_pubs.id'], ),
    sa.ForeignKeyConstraint(['noun_chunk_id'], ['noun_chunks.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('noun_chunk_word_lists',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('keyword_id', sa.Integer(), nullable=True),
    sa.Column('noun_chunk_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['keyword_id'], ['keywords.id'], ),
    sa.ForeignKeyConstraint(['noun_chunk_id'], ['noun_chunks.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('nounchunk_has_keyword')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('nounchunk_has_keyword',
    sa.Column('noun_chunk_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('keyword_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['keyword_id'], ['keywords.id'], name='nounchunk_has_keyword_keyword_id_fkey'),
    sa.ForeignKeyConstraint(['noun_chunk_id'], ['noun_chunks.id'], name='nounchunk_has_keyword_noun_chunk_id_fkey')
    )
    op.drop_table('noun_chunk_word_lists')
    op.drop_table('noun_chunk_lists')
    op.drop_table('keyword_lists')
    # ### end Alembic commands ###