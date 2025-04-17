import io
from typing import List, NoReturn
import pandas as pd
import sqlalchemy as sq
from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.base import generate_snowflake_id
from src.infrastructure.services.pandas_parser.drug.exc import (
    InvalidFileFormat, InvalidParsedData, MissingPreExecutionError)


class PandasParser(ABC):
    def __init__(self, file: io.BytesIO):
        self._file: io.BytesIO = file
        self._df: pd.DataFrame | None = None
        self._open_and_validate()

    @abstractmethod
    def _open(self) -> pd.DataFrame:
        raise NotImplemented("This is an abstract method")

    @abstractmethod
    def _required_columns(self) -> List[str]:
        raise NotImplemented("This is an abstract method")

    @abstractmethod
    def parse(self) -> NoReturn:
        raise NotImplemented("This is an abstract method")
    
    def _open_and_validate(self):
        try:
            self._df = self._open()

            required_columns = self._required_columns()
            if not all([col in self._df.columns for col in required_columns]):
                raise InvalidFileFormat()
        except Exception:
            raise InvalidFileFormat("Invalid file format or missing required columns")

    async def save_all(self, session: AsyncSession, catalog_id: int):
        if self._df is None:
            raise MissingPreExecutionError(
                "parse() must be called before insert()")

        required_columns = ["drug_name", "drug_code", "properties"]
        if not all([col in self._df.columns for col in required_columns]):
            raise InvalidParsedData("Invalid dataframe columns")

        if not all([
            self._df['drug_name'].apply(lambda x: isinstance(x, str)).all(),
            self._df['drug_code'].apply(lambda x: isinstance(x, str)).all(),
            self._df['properties'].apply(lambda x: isinstance(x, dict)).all(),
        ]):
            raise InvalidParsedData("Invalid data types in dataframe")

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
