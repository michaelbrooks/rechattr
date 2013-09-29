"""update question triggering

Revision ID: 211559e302c7
Revises: 439d1875bec5
Create Date: 2013-04-25 16:11:29.564000

"""

# revision identifiers, used by Alembic.
revision = '211559e302c7'
down_revision = '439d1875bec5'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('questions', sa.Column('trigger_manual', sa.Boolean(), nullable=True))
    op.add_column('questions', sa.Column('trigger_seconds', sa.Float(), nullable=True))
    op.drop_column('questions', u'trigger_type')
    op.drop_column('questions', u'trigger_info')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('questions', sa.Column(u'trigger_info', sa.VARCHAR(), nullable=True))
    op.add_column('questions', sa.Column(u'trigger_type', sa.VARCHAR(), nullable=True))
    op.drop_column('questions', 'trigger_seconds')
    op.drop_column('questions', 'trigger_manual')
    ### end Alembic commands ###