import pandas as pd
import sqlalchemy as sq
from io import BytesIO
from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.base import generate_snowflake_id


class MissingPreExecutionError(Exception):
    ...


class Parser(ABC):
    def __init__(self, file: BytesIO):
        self._file: BytesIO = file
        self._df: pd.DataFrame | None = None
        self._open_and_validate()

    @abstractmethod
    def _open_and_validate(self) -> bool:
        """Raise ValueError if the file is not valid or if it is missing a required field."""
        ...

    @abstractmethod
    def parse(self):
        ...

    async def save_all(self, session: AsyncSession, catalog_id: int):
        if self._df is None:
            raise MissingPreExecutionError(
                "parse() must be called before insert()")

        if not all([
            self._df['drug_name'].apply(lambda x: isinstance(x, str)).all(),
            self._df['drug_code'].apply(lambda x: isinstance(x, str)).all(),
            self._df['properties'].apply(lambda x: isinstance(x, dict)).all(),
        ]):
            raise ValueError("Invalid data types in dataframe")

        self._df["catalog_id"] = catalog_id
        self._df['id'] = self._df.apply(
            lambda _: generate_snowflake_id(), axis=1)

        conn = await session.connection()
        await conn.run_sync(
            lambda sync_conn: self._df.to_sql(
                'drugs', con=sync_conn, if_exists='append',
                index=False, dtype={"properties": sq.JSON}
            ),
        )
        await session.commit()
