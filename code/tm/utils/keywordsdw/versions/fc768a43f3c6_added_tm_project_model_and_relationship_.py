"""added tm project model and relationship to the researcher

Revision ID: fc768a43f3c6
Revises: b0cfef8ac496
Create Date: 2018-08-26 23:48:31.042499

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fc768a43f3c6'
down_revision = 'b0cfef8ac496'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tm_researcher_project',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.Text(), nullable=True),
    sa.Column('year', sa.Integer(), nullable=True),
    sa.Column('is_leader', sa.Boolean(), nullable=True),
    sa.Column('researcher_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['researcher_id'], ['tm_researcher_profile.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('tm_researcher_profile', sa.Column('project_id', sa.Integer(), nullable=True))
    op.create_unique_constraint('tm_researcher_profile_profile_id_key', 'tm_researcher_profile', ['profile_id'])
    op.create_foreign_key('tm_researcher_profile_project_id_fkey', 'tm_researcher_profile', 'tm_researcher_project', ['project_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('tm_researcher_profile_project_id_fkey', 'tm_researcher_profile', type_='foreignkey')
    op.drop_constraint('tm_researcher_profile_profile_id_key', 'tm_researcher_profile', type_='unique')
    op.drop_column('tm_researcher_profile', 'project_id')
    op.drop_table('tm_researcher_project')
    # ### end Alembic commands ###