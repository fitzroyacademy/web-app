"""add column for auth0 id

Revision ID: 1689dccdccc1
Revises: 0ba154a101c9
Create Date: 2020-05-30 15:30:26.896400

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1689dccdccc1'
down_revision = '0ba154a101c9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('auth0_id', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'auth0_id')
    # ### end Alembic commands ###