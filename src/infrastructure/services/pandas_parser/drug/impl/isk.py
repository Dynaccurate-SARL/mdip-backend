import pandas as pd

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser


class SK_Parser(PandasParser):
    def _open(self):
        return pd.read_excel(self._file, engine="xlrd")

    def _required_columns(self):
        return ["ŠÚKL kód", "Názov"]

    def parse(self):
        self._df["properties"] = self._df.apply(
            lambda row: row.drop(["ŠÚKL kód", "Názov"]).dropna().to_dict(), axis=1
        )

        # Select relevant columns
        self._df = self._df[["ŠÚKL kód", "Názov", "properties"]]
        self._df.rename(
            columns={
                "ŠÚKL kód": "drug_code",
                "Názov": "drug_name",
                "properties": "properties",
            },
            inplace=True,
        )
