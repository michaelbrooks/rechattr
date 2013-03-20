"""add human poll code field

Revision ID: 48057135376a
Revises: 3344607c54b5
Create Date: 2013-03-19 22:57:18.173000

"""

# revision identifiers, used by Alembic.
revision = '48057135376a'
down_revision = '3344607c54b5'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('polls', sa.Column('poll_url_human', sa.String(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('polls', 'poll_url_human')
    ### end Alembic commands ###
