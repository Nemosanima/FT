"""added profile picture

Revision ID: 224863ffce58
Revises: 
Create Date: 2023-05-22 11:42:14.663262

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '224863ffce58'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('profile_picture', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('profile_picture')

    # ### end Alembic commands ###