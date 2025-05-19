"""
Alembic migration: add language column to users table
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_language_to_user'
down_revision = '44c34cbf601b'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users', sa.Column('language', sa.String(length=5), nullable=True, server_default='ua'))

def downgrade():
    op.drop_column('users', 'language')
