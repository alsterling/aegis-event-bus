"""create audit_log

Revision ID: bd536313df34
Revises:
Create Date: 2025-07-13 22:18:24.110812

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "bd536313df34"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_auditlog_job_id"), table_name="auditlog")
    op.drop_table("auditlog")
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "auditlog",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("job_id", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column("action", sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column(
            "timestamp",
            postgresql.TIMESTAMP(timezone=True),
            autoincrement=False,
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("auditlog_pkey")),
    )
    op.create_index(op.f("ix_auditlog_job_id"), "auditlog", ["job_id"], unique=False)
    # ### end Alembic commands ###
