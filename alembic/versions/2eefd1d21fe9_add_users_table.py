"""add users table

Revision ID: 2eefd1d21fe9
Revises: 39dc751adeff
Create Date: 2013-03-25 00:45:59.841000

"""

# revision identifiers, used by Alembic.
revision = '2eefd1d21fe9'
down_revision = '39dc751adeff'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('oauth_key', sa.String(), nullable=True),
    sa.Column('oauth_secret', sa.String(), nullable=True),
    sa.Column('oauth_user_id', sa.BigInteger(), nullable=True),
    sa.Column('oauth_provider', sa.String(), nullable=True),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('full_name', sa.String(), nullable=True),
    sa.Column('last_signed_in', sa.DateTime(), nullable=True),
    sa.Column('tweet_count', sa.Integer(), nullable=True),
    sa.Column('response_count', sa.Integer(), nullable=True),
    sa.Column('user_cache', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    ### end Alembic commands ###
