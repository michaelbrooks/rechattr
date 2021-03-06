"""Add basic tables

Revision ID: 175747a10ed
Revises: None
Create Date: 2013-03-04 18:52:50.575000

"""

# revision identifiers, used by Alembic.
revision = '175747a10ed'
down_revision = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('polls',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated', sa.DateTime(timezone=True), nullable=True),
        sa.Column('user_email', sa.String(), nullable=True),
        sa.Column('event_start', sa.DateTime(timezone=True), nullable=True),
        sa.Column('event_stop', sa.DateTime(timezone=True), nullable=True),
        sa.Column('twitter_terms', sa.String(), nullable=True),
        sa.Column('poll_url_code', sa.String(), nullable=True),
        sa.Column('results_url_code', sa.String(), nullable=True),
        sa.Column('edit_url_code', sa.String(), nullable=True),
        sa.Column('poll_short_url', sa.String(), nullable=True),
        sa.Column('definition', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tweets',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('created', sa.DateTime(timezone=True), nullable=True),
        sa.Column('poll_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.BigInteger(), nullable=True),
        sa.Column('screen_name', sa.String(), nullable=True),
        sa.Column('user_name', sa.String(), nullable=True),
        sa.Column('text', sa.String(), nullable=True),
        sa.Column('retweet_of_status_id', sa.BigInteger(), nullable=True),
        sa.Column('reply_to_tweet_id', sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(['poll_id'], ['polls.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('visits',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created', sa.DateTime(timezone=True), nullable=True),
        sa.Column('poll_id', sa.Integer(), nullable=True),
        sa.Column('url', sa.String(), nullable=True),
        sa.Column('page', sa.String(), nullable=True),
        sa.Column('ip_address', postgresql.INET(), nullable=True),
        sa.Column('device', sa.String(), nullable=True),
        sa.Column('browser', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['poll_id'], ['polls.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('responses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('created', sa.DateTime(timezone=True), nullable=True),
        sa.Column('poll_id', sa.Integer(), nullable=True),
        sa.Column('visit_id', sa.Integer(), nullable=True),
        sa.Column('answers', sa.String(), nullable=True),
        sa.Column('comment', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['poll_id'], ['polls.id'], ),
        sa.ForeignKeyConstraint(['visit_id'], ['visits.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('responses')
    op.drop_table('visits')
    op.drop_table('tweets')
    op.drop_table('polls')
    ### end Alembic commands ###
