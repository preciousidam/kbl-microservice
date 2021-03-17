"""empty message

Revision ID: c9a8bc6b8467
Revises: 
Create Date: 2021-03-16 22:52:17.991332

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c9a8bc6b8467'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('leave',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('ro', sa.String(length=255), nullable=False),
    sa.Column('roe', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('date',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('start', sa.Date(), nullable=False),
    sa.Column('end', sa.Date(), nullable=False),
    sa.Column('leave_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['leave_id'], ['leave.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('date')
    op.drop_table('leave')
    # ### end Alembic commands ###
