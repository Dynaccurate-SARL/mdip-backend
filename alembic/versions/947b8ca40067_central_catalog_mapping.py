"""'database view to track central catalog mappings in each drug'

Revision ID: 947b8ca40067
Revises: 352f8e72b22c
Create Date: 2025-05-04 03:09:32.510459

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '947b8ca40067'
down_revision: Union[str, None] = '352f8e72b22c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    drug_catalogs = sa.table(
        'drug_catalogs',
        sa.column('id', sa.BigInteger),
        sa.column('name', sa.String),
        sa.column('is_central', sa.Boolean),
    )
    drugs = sa.table(
        'drugs',
        sa.column('id', sa.BigInteger),
        # foreign key to drug_catalogs.id
        sa.column('catalog_id', sa.BigInteger),
        sa.column('drug_name', sa.String),
        sa.column('drug_code', sa.String),
    )
    mappings = sa.table(
        'drug_mappings',
        # foreign key to drugs.id
        sa.column('drug_id', sa.BigInteger),
        # foreign key to drugs.id
        sa.column('related_drug_id', sa.BigInteger),
    )

    view_query = sa.select(
        drugs.c.id.label('drug_id'),
        drugs.c.drug_name.label('drug_name'),
        drugs.c.drug_code.label('drug_code'),
        sa.func.count(mappings.c.related_drug_id).label('mapping_count')
    ).select_from(
        drugs
        .join(drug_catalogs, drugs.c.catalog_id == drug_catalogs.c.id)
        .outerjoin(mappings, mappings.c.drug_id == drugs.c.id)
    ).where(
        drug_catalogs.c.is_central.is_(True)
    ).group_by(
        drugs.c.id,
        drugs.c.drug_name
    ).order_by(
        drugs.c.id
    )

    compiled_sql = view_query.compile(compile_kwargs={"literal_binds": True})
    op.execute(f"CREATE VIEW drug_mappings_stats AS {compiled_sql}")


def downgrade() -> None:
    op.execute("DROP VIEW drug_mappings_stats")
