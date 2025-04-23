import io
import pandas as pd
from pydantic import BaseModel
from typing import Any, Generator, List

from src.infrastructure.services.pandas_parser.drug.exc import InvalidFileFormat

class DrugMapping(BaseModel):
    drug_code: str
    related_drug_code: str

class MappingParser:
    def __init__(self, file_bytes: bytes):
        self._file = io.BytesIO(file_bytes)
        self._df: pd.DataFrame | None = None
        self._open_and_validate()

    def _required_columns(self) -> List[str]:
        return ["drug_code", "related_drug_code"]

    def _open_and_validate(self):
        try:
            self._df = pd.read_csv(self._file, delimiter=',')

            required_columns = self._required_columns()
            if not all([col in self._df.columns for col in required_columns]):
                raise InvalidFileFormat()
        except Exception as err:
            raise InvalidFileFormat("Invalid file format or missing required columns")

    def parse(self) -> Generator[list[DrugMapping], Any, None]:
        for i in range(0, len(self._df), 100):
            chunk = self._df.iloc[i:i + 100][["drug_code", "related_drug_code"]]
            records = chunk.to_dict(orient="records")
            yield [DrugMapping(**record) for record in records]

