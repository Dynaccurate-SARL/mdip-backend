import io
import traceback
import pandas as pd
from typing import List, NoReturn
from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.drug import Drug
from src.infrastructure.services.pandas_parser.drug.exc import (
    InvalidFileFormat,
    InvalidParsedData,
    MissingPreExecutionError,
)


class PandasParser(ABC):
    def __init__(self, source: io.BytesIO | str):
        self._file = source
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
            print(traceback.format_exc())
            raise InvalidFileFormat("Invalid file format")

        r_columns = self._required_columns()
        df_columns = self._df.columns.tolist()
        missing = [item for item in r_columns if item not in df_columns]
        if missing:
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

        for idx, (_, row) in enumerate(self._df.iterrows(), start=1):
            drug = Drug(
                catalog_id=catalog_id,
                drug_code=str(row["drug_code"]),
                drug_name=str(row["drug_name"]),
                properties=row["properties"],
            )
            session.add(drug)
            # Commit every 100 rows
            if idx % 100 == 0:
                await session.commit()
        # Commit the remaining rows
        if len(self._df) % 100 != 0:
            await session.commit()
