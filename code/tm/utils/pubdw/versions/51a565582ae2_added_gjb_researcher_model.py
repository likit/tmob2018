"""added gjb researcher model

Revision ID: 51a565582ae2
Revises: cf68bab4b975
Create Date: 2018-10-08 07:42:04.049415

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '51a565582ae2'
down_revision = 'cf68bab4b975'
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
    sa.Column('gender', sa.String(length=1), nullable=True),
    sa.Column('email', sa.String(length=128), nullable=True),
    sa.Column('major_th', sa.String(length=255), nullable=True),
    sa.Column('faculty_th', sa.String(length=255), nullable=True),
    sa.Column('university_th', sa.String(length=255), nullable=True),
    sa.Column('thesis_title_th', sa.Text(), nullable=True),
    sa.Column('thesis_title_en', sa.Text(), nullable=True),
    sa.Column('thesis_finished', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('gjb_researcher_profile')
    # ### end Alembic commands ###
