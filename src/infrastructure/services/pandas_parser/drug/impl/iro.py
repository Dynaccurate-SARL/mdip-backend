import pandas as pd

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser


class RO_Parser(PandasParser):
    def _open(self):
        return pd.read_excel(self._file, engine='openpyxl')

    def _required_columns(self):
        return ["Cod CIM", "Denumire comerciala"]

    def parse(self):
        self._df["properties"] = self._df.apply(lambda row: row.drop(
            ["Cod CIM", "Denumire comerciala"]).dropna().to_dict(), axis=1)
        
        # Select relevant columns
        self._df = self._df[["Cod CIM", "Denumire comerciala", "properties"]]
        self._df.rename(columns={
            "Cod CIM": "drug_code",
            "Denumire comerciala": "drug_name",
            "properties": "properties"
        }, inplace=True)
