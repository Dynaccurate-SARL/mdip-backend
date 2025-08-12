import pandas as pd

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser


class BG_Parser(PandasParser):
    def _open(self):
        return pd.read_excel(self._file, engine="openpyxl", dtype=str)

    def _required_columns(self):
        return ["Търговско име"]

    def parse(self):

        self._df["ID"] = [f"BG_{i + 1}" for i in range(len(self._df))]

        if self._df.columns[0].startswith("Unnamed"):
            self._df = self._df.drop(self._df.columns[0], axis=1)
        
        self._df["properties"] = self._df.apply(
            lambda row: row.drop(["ID", "Търговско име"]).dropna().to_dict(), axis=1
        )

        # Select relevant columns
        self._df = self._df[["ID", "Търговско име", "properties"]]
        self._df.rename(
            columns={
                "ID": "drug_code",
                "Търговско име": "drug_name",
                "properties": "properties",
            },
            inplace=True,
        )

        self._df = self._df.dropna()
