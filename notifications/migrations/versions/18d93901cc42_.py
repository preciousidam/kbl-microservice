"""empty message

Revision ID: 18d93901cc42
Revises: cb0ea4f463a8
Create Date: 2021-03-16 23:13:25.897150

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '18d93901cc42'
down_revision = 'cb0ea4f463a8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('notification', sa.Column('when', sa.Date(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('notification', 'when')
    # ### end Alembic commands ###
