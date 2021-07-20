"""users table

Revision ID: 7f0a57912e4c
Revises: 0bc84c786665
Create Date: 2020-05-12 08:29:44.895199

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7f0a57912e4c'
down_revision = '0bc84c786665'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_user_role', table_name='user')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ix_user_role', 'user', ['role'], unique=1)
    # ### end Alembic commands ###
