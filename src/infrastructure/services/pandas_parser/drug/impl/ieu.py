import pandas as pd

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser


class EU_Parser(PandasParser):
    def _open(self):
        return pd.read_excel(self._file, engine="openpyxl", skiprows=8, dtype=str)

    def _required_columns(self):
        return ["EMA product number", "Name of medicine", "Category"]

    def parse(self):

        self._df = self._df[self._df["Category"] != "Veterinary"]

        # Convert to JSON-like format for properties
        self._df["properties"] = self._df.apply(
            lambda row: row.drop(
                ["EMA product number", "Name of medicine"]
            ).dropna().to_dict(),
            axis=1,
        )

        # Select relevant columns
        self._df = self._df[["EMA product number",
                             "Name of medicine", "properties"]]
        self._df.rename(
            columns={
                "EMA product number": "drug_code",
                "Name of medicine": "drug_name",
                "properties": "properties",
            },
            inplace=True,
        )

        self._df = self._df.dropna()
