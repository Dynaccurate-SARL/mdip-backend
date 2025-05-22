import pandas as pd

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser


class SE_Parser(PandasParser):
    def _open(self):
        return pd.read_excel(self._file, engine="openpyxl")

    def _required_columns(self):
        return ["NPL-id", "Namn"]

    def parse(self):
        self._df["properties"] = self._df.apply(
            lambda row: row.drop(["NPL-id", "Namn"]).dropna().to_dict(), axis=1
        )

        # Select relevant columns
        self._df = self._df[["NPL-id", "Namn", "properties"]]
        self._df.rename(
            columns={
                "NPL-id": "drug_code",
                "Namn": "drug_name",
                "properties": "properties",
            },
            inplace=True,
        )
