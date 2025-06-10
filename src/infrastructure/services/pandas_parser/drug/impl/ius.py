import pandas as pd

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser
from src.utils.file import detect_file_encoding


class US_Parser(PandasParser):
    def _open(self):
        encoding = detect_file_encoding(self._file)
        return pd.read_csv(
            self._file, delimiter="\t", encoding=encoding, on_bad_lines="skip", dtype=str
        ).where(pd.notnull, None)

    def _required_columns(self):
        return ["DrugName"]

    def parse(self):
        self._df["ID"] = [f"US_{i + 1}" for i in range(len(self._df))]

        self._df["properties"] = self._df.apply(
            lambda row: row.drop(["ID", "DrugName"]).dropna().to_dict(), axis=1
        )

        # Select relevant columns
        self._df = self._df[["ID", "DrugName", "properties"]]
        self._df.rename(
            columns={
                "ID": "drug_code",
                "DrugName": "drug_name",
                "properties": "properties",
            },
            inplace=True,
        )

        self._df = self._df.dropna()
