"""merge heads for language column

Revision ID: c6b61110cf54
Revises: 469c26a02fb6, add_language_to_user
Create Date: 2025-05-19 12:23:14.513451

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c6b61110cf54'
down_revision = ('469c26a02fb6', 'add_language_to_user')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
