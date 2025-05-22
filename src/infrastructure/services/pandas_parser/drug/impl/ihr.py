import pandas as pd

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser


class HR_Parser(PandasParser):
    def _open(self):
        return pd.read_excel(self._file, skiprows=9, engine="openpyxl")

    def _required_columns(self):
        return ["Naziv"]

    def parse(self):
        self._df["ID"] = [f"HR_{i + 1}" for i in range(len(self._df))]

        self._df["properties"] = self._df.apply(
            lambda row: row.drop(["ID", "Naziv"]).dropna().to_dict(), axis=1
        )

        self._df = self._df[["ID", "Naziv", "properties"]]
        self._df.rename(
            columns={
                "ID": "drug_code",
                "Naziv": "drug_name",
                "properties": "properties",
            },
            inplace=True,
        )
