"""added TM Researcher Profile to the model

Revision ID: b0cfef8ac496
Revises: 0ce6845adce3
Create Date: 2018-08-26 15:50:47.204485

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b0cfef8ac496'
down_revision = '0ce6845adce3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tm_researcher_profile',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name_th', sa.String(length=255), nullable=True),
    sa.Column('last_name_th', sa.String(length=255), nullable=True),
    sa.Column('first_name_en', sa.String(length=255), nullable=True),
    sa.Column('last_name_en', sa.String(length=255), nullable=True),
    sa.Column('profile_id', sa.Integer(), nullable=True),
    sa.Column('gender', sa.String(length=1), nullable=True),
    sa.Column('dob', sa.Date(), nullable=True),
    sa.Column('isRegistered', sa.Boolean(), nullable=True),
    sa.Column('email', sa.String(length=128), nullable=True),
    sa.Column('scholarship_info_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['scholarship_info_id'], ['scholarship_info.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('tm_researcher_profile')
    # ### end Alembic commands ###