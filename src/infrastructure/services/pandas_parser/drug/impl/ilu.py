import pandas as pd

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser


class LU_Parser(PandasParser):
    def _open(self):
        return pd.read_excel(self._file, skiprows=2, engine="openpyxl", dtype=str)

    def _required_columns(self):
        return ["Nr. AMM", "Dénomination"]

    def parse(self):
        self._df["properties"] = self._df.apply(
            lambda row: row.drop(["Nr. AMM", "Dénomination"]).dropna().to_dict(), axis=1
        )

        self._df = self._df[["Nr. AMM", "Dénomination", "properties"]]
        self._df.rename(
            columns={
                "Nr. AMM": "drug_code",
                "Dénomination": "drug_name",
                "properties": "properties",
            },
            inplace=True,
        )

        self._df = self._df.dropna()
