import sqlalchemy as sq

from src.domain.entities import Base, generate_snowflake_id


class DrugCatalog(Base):
    __tablename__ = 'drug_catalogs'

    id = sq.Column(sq.BigInteger, primary_key=True,
                   default=generate_snowflake_id)
    name = sq.Column(sq.String(255), nullable=False)
    country = sq.Column(sq.String(100), nullable=False)
    version = sq.Column(sq.Integer, nullable=False, default=1)
    notes = sq.Column(sq.Text, nullable=True)
    file_transaction_id = sq.Column(sq.String(36), nullable=True)
