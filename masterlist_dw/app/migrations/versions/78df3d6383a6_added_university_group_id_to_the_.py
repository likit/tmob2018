"""added university group id to the reseaearcher table

Revision ID: 78df3d6383a6
Revises: 1be024416046
Create Date: 2019-12-22 13:48:34.583110

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '78df3d6383a6'
down_revision = '1be024416046'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('dim_university_groups',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('br_university_groups',
    sa.Column('university_group_id', sa.Integer(), nullable=False),
    sa.Column('university_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['university_group_id'], ['dim_university_groups.id'], ),
    sa.ForeignKeyConstraint(['university_id'], ['dim_universities.id'], ),
    sa.PrimaryKeyConstraint('university_group_id', 'university_id')
    )
    op.add_column('fact_researchers', sa.Column('university_group_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'fact_researchers', 'dim_university_groups', ['university_group_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'fact_researchers', type_='foreignkey')
    op.drop_column('fact_researchers', 'university_group_id')
    op.drop_table('br_university_groups')
    op.drop_table('dim_university_groups')
    # ### end Alembic commands ###
