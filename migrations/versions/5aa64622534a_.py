"""empty message

Revision ID: 5aa64622534a
Revises: 31c4c877f51f
Create Date: 2022-02-16 11:13:31.827235

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5aa64622534a'
down_revision = '31c4c877f51f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('la_t_User', 'CreatedById')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('la_t_User', sa.Column('CreatedById', sa.INTEGER(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
