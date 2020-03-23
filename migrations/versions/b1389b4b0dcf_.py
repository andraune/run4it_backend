"""empty message

Revision ID: b1389b4b0dcf
Revises: 8247d45cbacb
Create Date: 2020-03-02 21:54:46.602341

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b1389b4b0dcf'
down_revision = '8247d45cbacb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('training_goal_categories', sa.Column('unit', sa.String(length=16), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('training_goal_categories', 'unit')
    # ### end Alembic commands ###