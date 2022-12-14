"""empty message

Revision ID: 19ffc98d10e5
Revises: 4a6c3f445c25
Create Date: 2022-08-05 10:09:44.525249

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '19ffc98d10e5'
down_revision = '4a6c3f445c25'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('shows',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.DateTime(), nullable=False),
    sa.Column('artist_id', sa.Integer(), nullable=False),
    sa.Column('venue_id', sa.Integer(), nullable=False),
    sa.Column('upcoming', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['artist.id'], ),
    sa.ForeignKeyConstraint(['venue_id'], ['venue.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('artist', sa.Column('no_of_upcoming_shows', sa.Integer(), nullable=True))
    op.add_column('artist', sa.Column('no_of_past_shows', sa.Integer(), nullable=True))
    op.add_column('venue', sa.Column('no_of_upcoming_shows', sa.Integer(), nullable=True))
    op.add_column('venue', sa.Column('no_of_past_shows', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venue', 'no_of_past_shows')
    op.drop_column('venue', 'no_of_upcoming_shows')
    op.drop_column('artist', 'no_of_past_shows')
    op.drop_column('artist', 'no_of_upcoming_shows')
    op.drop_table('shows')
    # ### end Alembic commands ###
