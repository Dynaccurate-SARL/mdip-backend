import pandas as pd

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser


class EU_Parser(PandasParser):
    def _open(self):
        return pd.read_excel(self._file, engine="openpyxl", skiprows=4)

    def _required_columns(self):
        return ["ProductNumber", "ProductName"]

    def parse(self):
        # Strip whitespace from column names
        self._df.columns = self._df.columns.str.strip()

        # Convert to JSON-like format for properties
        self._df["properties"] = self._df.apply(
            lambda row: row.drop(["ProductNumber", "ProductName"]).dropna().to_dict(),
            axis=1,
        )

        # Select relevant columns
        self._df = self._df[["ProductNumber", "ProductName", "properties"]]
        self._df.rename(
            columns={
                "ProductNumber": "drug_code",
                "ProductName": "drug_name",
                "properties": "properties",
            },
            inplace=True,
        )
