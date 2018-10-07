"""added GJB researcher profile model and the thesis model

Revision ID: 7bb5aef25e79
Revises: fc768a43f3c6
Create Date: 2018-10-07 06:26:36.765351

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7bb5aef25e79'
down_revision = 'fc768a43f3c6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('gjb_researcher_profile',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title_th', sa.String(length=32), nullable=True),
    sa.Column('title_en', sa.String(length=32), nullable=True),
    sa.Column('first_name_th', sa.String(length=255), nullable=True),
    sa.Column('last_name_th', sa.String(length=255), nullable=True),
    sa.Column('first_name_en', sa.String(length=255), nullable=True),
    sa.Column('last_name_en', sa.String(length=255), nullable=True),
    sa.Column('profile_id', sa.Integer(), nullable=True),
    sa.Column('gender', sa.String(length=1), nullable=True),
    sa.Column('email', sa.String(length=128), nullable=True),
    sa.Column('major_th', sa.String(length=255), nullable=True),
    sa.Column('faculty_th', sa.String(length=255), nullable=True),
    sa.Column('university_th', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('profile_id')
    )
    op.create_table('gjb_theses',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title_th', sa.Text(), nullable=True),
    sa.Column('title_en', sa.Text(), nullable=True),
    sa.Column('finished', sa.Boolean(), nullable=True),
    sa.Column('researcher_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['researcher_id'], ['gjb_researcher_profile.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('gjb_theses')
    op.drop_table('gjb_researcher_profile')
    # ### end Alembic commands ###