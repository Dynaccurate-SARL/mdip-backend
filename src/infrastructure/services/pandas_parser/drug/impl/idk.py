import pandas as pd

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser


class DK_Parser(PandasParser):
    def _open(self):
        return pd.read_excel(self._file, engine="openpyxl")

    def _required_columns(self):
        return ["Drugid", "Navn"]

    def parse(self):        
        try:
            self._df["Registreringsdato"] = self._df["Registreringsdato"].dt.strftime(
                "%Y-%m-%d"
            )
        except KeyError:
            ...
        
        self._df = self._df.dropna(thresh=3)

        self._df["properties"] = self._df.apply(
            lambda row: row.drop(["Drugid", "Navn"]).dropna().to_dict(), axis=1
        )

        # Select relevant columns
        self._df = self._df[["Drugid", "Navn", "properties"]]
        self._df.rename(
            columns={
                "Drugid": "drug_code",
                "Navn": "drug_name",
                "properties": "properties",
            },
            inplace=True,
        )
        
        self._df = self._df.dropna()
