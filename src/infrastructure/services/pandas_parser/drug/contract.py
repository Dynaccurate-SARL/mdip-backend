import io
import pandas as pd
import sqlalchemy as sq
from typing import List, NoReturn
from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.db.base import generate_snowflake_id
from src.infrastructure.services.pandas_parser.drug.exc import (
    InvalidFileFormat,
    InvalidParsedData,
    MissingPreExecutionError,
)


class PandasParser(ABC):
    def __init__(self, file_bytes: io.BytesIO):
        self._file = file_bytes
        self._df: pd.DataFrame | None = None
        self._open_and_validate()

    @abstractmethod
    def _open(self) -> pd.DataFrame:
        raise NotImplementedError("This is an abstract method")

    @abstractmethod
    def _required_columns(self) -> List[str]:
        raise NotImplementedError("This is an abstract method")

    @abstractmethod
    def parse(self) -> NoReturn:
        raise NotImplementedError("This is an abstract method")

    def _open_and_validate(self):
        try:
            self._df = self._open()
        except Exception as err:
            print(f"Error opening file: {err}")
            # print(traceback.format_exc())
            raise InvalidFileFormat("Invalid file format")

        r_columns = self._required_columns()
        df_columns = self._df.columns.tolist()
        missing = [item for item in r_columns if item not in df_columns]
        if missing:
            # print(f"Dataframe columns: {df_columns}")
            # print(f"Required columns: {r_columns}")
            raise InvalidFileFormat(f"Missing required columns: {missing}")

    async def save_all(self, session: AsyncSession, catalog_id: int):
        if self._df is None:
            raise MissingPreExecutionError(
                "parse() must be called before insert()")

        required_columns = ["drug_name", "drug_code", "properties"]
        if not all([col in self._df.columns for col in required_columns]):
            raise InvalidParsedData("Invalid dataframe columns")

        # Ensure that the data types are correct
        self._df["drug_name"].apply(lambda x: str(x))
        self._df["drug_code"].apply(lambda x: str(x))

        # Could be redundant, but it's a good idea to check
        if not all(
            [
                self._df["drug_name"].apply(
                    lambda x: isinstance(x, str)).all(),
                self._df["drug_code"].apply(
                    lambda x: isinstance(x, str)).all(),
                self._df["properties"].apply(
                    lambda x: isinstance(x, dict)).all(),
            ]
        ):
            raise InvalidParsedData("Invalid data types in dataframe")

        self._df["catalog_id"] = catalog_id
        self._df["id"] = self._df.apply(
            lambda _: generate_snowflake_id(), axis=1)

        conn = await session.connection()
        await conn.run_sync(
            lambda sync_conn: self._df.to_sql(  # type: ignore
                "drugs",
                con=sync_conn,
                if_exists="append",
                index=False,
                dtype={"properties": sq.JSON},
            ),
        )
        await session.commit()
