import pandas as pd

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser


class PT_Parser(PandasParser):
    def _open(self):
        return pd.read_excel(self._file, engine="openpyxl")

    def _required_columns(self):
        return ["Nome do Medicamento"]

    def parse(self):
        self._df["ID"] = [f"PT_{i + 1}" for i in range(len(self._df))]

        self._df["properties"] = self._df.apply(
            lambda row: row.drop(["ID", "Nome do Medicamento"]).dropna().to_dict(),
            axis=1,
        )

        # Select relevant columns
        self._df = self._df[["ID", "Nome do Medicamento", "properties"]]
        self._df.rename(
            columns={
                "ID": "drug_code",
                "Nome do Medicamento": "drug_name",
                "properties": "properties",
            },
            inplace=True,
        )
