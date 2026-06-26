"""initial

Revision ID: 2afa4447f706
Revises: 
Create Date: 2026-06-26 16:43:41.020580

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '2afa4447f706'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass