"""add days_needed to loan_requests and make due_at nullable

Revision ID: a1b2c3d4e5f6
Revises: 0e01b7542e26
Create Date: 2026-03-04 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '0e01b7542e26'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('loan_requests') as batch_op:
        batch_op.add_column(sa.Column('days_needed', sa.Integer(), nullable=True))
        batch_op.alter_column('due_at', existing_type=sa.DateTime(timezone=True), nullable=True)


def downgrade() -> None:
    with op.batch_alter_table('loan_requests') as batch_op:
        batch_op.alter_column('due_at', existing_type=sa.DateTime(timezone=True), nullable=False)
        batch_op.drop_column('days_needed')
