"""empty message

Revision ID: 89b77ca0f1c4
Revises: 
Create Date: 2022-12-07 09:34:19.413407

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '89b77ca0f1c4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('cluster',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=256), nullable=False),
    sa.Column('cluster_id', sa.String(length=256), nullable=False),
    sa.Column('ip_address', sa.String(length=256), nullable=False),
    sa.Column('port', sa.Integer(), nullable=False),
    sa.Column('chosen_cluster', sa.String(length=256), nullable=True),
    sa.Column('date_created', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('cluster_id'),
    sa.UniqueConstraint('ip_address'),
    sa.UniqueConstraint('name')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=256), nullable=True),
    sa.Column('username', sa.String(length=256), nullable=False),
    sa.Column('password', sa.String(length=256), nullable=False),
    sa.Column('date_created', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user')
    op.drop_table('cluster')
    # ### end Alembic commands ###
