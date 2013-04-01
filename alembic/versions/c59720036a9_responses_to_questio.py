"""responses to questions

Revision ID: c59720036a9
Revises: 5a67bf5f6af4
Create Date: 2013-04-01 08:38:33.444000

"""

# revision identifiers, used by Alembic.
revision = 'c59720036a9'
down_revision = '5a67bf5f6af4'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(u'responses', u'answers', existing_type=sa.String(), 
                    name=u'answer')
    op.drop_column(u'responses', u'comment')
    
    op.add_column(u'responses', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
            "responses_user_id_fkey", "responses",
            "users", ["user_id"], ["id"])
            
    op.add_column(u'responses', sa.Column('question_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
            "responses_question_id_fkey", "responses",
            "questions", ["question_id"], ["id"])
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(u'responses', u'answer', existing_type=sa.String(), 
                    name=u'answers')
    op.add_column(u'responses', sa.Column(u'comment', sa.VARCHAR(), nullable=True))
    op.drop_column(u'responses', 'question_id')
    op.drop_column(u'responses', 'user_id')
    ### end Alembic commands ###
