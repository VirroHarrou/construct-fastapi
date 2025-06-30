"""Chat with timezone

Revision ID: e71f4bf03e60
Revises: a15e872d3bdd
Create Date: 2025-07-01 01:38:20.346282

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e71f4bf03e60'
down_revision: Union[str, Sequence[str], None] = 'a15e872d3bdd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
