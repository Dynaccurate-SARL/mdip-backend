import pandas as pd

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser


class CY_Parser(PandasParser):
    def _open(self):
        return pd.read_excel(self._file, engine="openpyxl", dtype=str)

    def _required_columns(self):
        return ["Code", "Name / Strength"]

    def parse(self):
        self._df["properties"] = self._df.apply(
            lambda row: row.drop(["Code", "Name / Strength"]).dropna().to_dict(), axis=1
        )

        # Select relevant columns
        self._df = self._df[["Code", "Name / Strength", "properties"]]
        self._df.rename(
            columns={
                "Code": "drug_code",
                "Name / Strength": "drug_name",
                "properties": "properties",
            },
            inplace=True,
        )

        self._df = self._df.dropna()
