"""olson field in poll

Revision ID: f652b66c641
Revises: 7644a90af11
Create Date: 2013-04-04 17:20:25.489000

"""

# revision identifiers, used by Alembic.
revision = 'f652b66c641'
down_revision = '7644a90af11'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('polls', sa.Column('olson_timezone', sa.String(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('polls', 'olson_timezone')
    ### end Alembic commands ###
