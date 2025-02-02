"""Add order column to Task model

Revision ID: 6d6b2c1cb215
Revises: 7a43a88d50d9
Create Date: 2024-09-14 14:04:07.039372

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6d6b2c1cb215'
down_revision = '7a43a88d50d9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.add_column(sa.Column('original_filename', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('saved_filename', sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column('order', sa.Integer(), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('task', schema=None) as batch_op:
        batch_op.drop_column('order')
        batch_op.drop_column('saved_filename')
        batch_op.drop_column('original_filename')

    # ### end Alembic commands ###
