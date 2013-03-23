"""tweet properties for display requirements

Revision ID: 59931c4ab451
Revises: 48057135376a
Create Date: 2013-03-23 00:00:53.483000

"""

# revision identifiers, used by Alembic.
revision = '59931c4ab451'
down_revision = '48057135376a'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tweets', sa.Column('entities', sa.String(), nullable=True))
    op.add_column('tweets', sa.Column('profile_image_url', sa.String(), nullable=True))
    op.add_column('tweets', sa.Column('utc_offset', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tweets', 'profile_image_url')
    op.drop_column('tweets', 'entities')
    op.drop_column('tweets', 'utc_offset')
    ### end Alembic commands ###
