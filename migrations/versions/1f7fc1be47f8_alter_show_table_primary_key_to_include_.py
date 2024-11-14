"""Alter show table primary key to include start_time

Revision ID: 1f7fc1be47f8
Revises: 
Create Date: 2024-11-13 15:46:45.715606

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1f7fc1be47f8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('show', schema=None) as batch_op:
        batch_op.create_unique_constraint('unique_show', ['venue_id', 'artist_id', 'start_time'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('show', schema=None) as batch_op:
        batch_op.drop_constraint('unique_show', type_='unique')

    # ### end Alembic commands ###