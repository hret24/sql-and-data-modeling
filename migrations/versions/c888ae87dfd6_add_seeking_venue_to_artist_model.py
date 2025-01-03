"""Add seeking_venue to Artist model

Revision ID: c888ae87dfd6
Revises: 4efe976943ef
Create Date: 2024-11-24 13:37:58.248419

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c888ae87dfd6'
down_revision = '4efe976943ef'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('venue_artist_association')
    with op.batch_alter_table('artist', schema=None) as batch_op:
        # Add new column
        batch_op.add_column(sa.Column('seeking_venue', sa.Boolean(), nullable=True))
        # Drop old column
        batch_op.drop_column('seeking_for_venue')
    
    # Rename column seeking_for_artist to seeking_artist
    with op.batch_alter_table('artist', schema=None) as batch_op:
        batch_op.alter_column(
            'seeking_for_artist',
            new_column_name='seeking_artist',
            existing_type=sa.Boolean
        )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('artist', schema=None) as batch_op:
        # Reverse rename of column seeking_artist to seeking_for_artist
        batch_op.alter_column(
            'seeking_artist',
            new_column_name='seeking_for_artist',
            existing_type=sa.Boolean
        )

        # Reverse drop of seeking_venue
        batch_op.add_column(sa.Column('seeking_for_venue', sa.BOOLEAN(), autoincrement=False, nullable=True))
        batch_op.drop_column('seeking_venue')

    # Recreate dropped table
    op.create_table('venue_artist_association',
    sa.Column('venue_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('artist_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['artist.id'], name='venue_artist_association_artist_id_fkey'),
    sa.ForeignKeyConstraint(['venue_id'], ['venue.id'], name='venue_artist_association_venue_id_fkey'),
    sa.PrimaryKeyConstraint('venue_id', 'artist_id', name='venue_artist_association_pkey')
    )
    # ### end Alembic commands ###
