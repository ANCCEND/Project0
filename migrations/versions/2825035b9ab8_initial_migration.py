"""Initial migration

Revision ID: 2825035b9ab8
Revises: 
Create Date: 2025-02-03 17:13:26.040967

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2825035b9ab8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('Username', sa.String(length=50), nullable=False),
    sa.Column('Email', sa.String(length=120), nullable=False),
    sa.Column('Password_hashed', sa.String(length=300), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('Email'),
    sa.UniqueConstraint('Username')
    )
    op.create_table('post',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('Title', sa.String(length=120), nullable=False),
    sa.Column('Content', sa.Text(), nullable=False),
    sa.Column('Category', sa.String(length=40), nullable=False),
    sa.Column('Date', sa.DateTime(), nullable=True),
    sa.Column('User_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['User_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('post')
    op.drop_table('user')
    # ### end Alembic commands ###
