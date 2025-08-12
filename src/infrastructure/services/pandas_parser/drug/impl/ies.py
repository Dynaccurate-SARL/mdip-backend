import pandas as pd

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser


class ES_Parser(PandasParser):
    def _open(self):
        return pd.read_excel(self._file, engine="openpyxl")

    def _required_columns(self):
        return ["Nº Registro", "Medicamento"]

    def parse(self):
        self._df["properties"] = self._df.apply(
            lambda row: row.drop(["Nº Registro", "Medicamento"]).dropna().to_dict(),
            axis=1,
        )

        # Select relevant columns
        self._df = self._df[["Nº Registro", "Medicamento", "properties"]]
        self._df.rename(
            columns={
                "Nº Registro": "drug_code",
                "Medicamento": "drug_name",
                "properties": "properties",
            },
            inplace=True,
        )
