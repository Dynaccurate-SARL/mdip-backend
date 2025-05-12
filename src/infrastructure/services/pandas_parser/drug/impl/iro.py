import pandas as pd

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser


class RO_Parser(PandasParser):
    def _open(self):
        return pd.read_excel(self._file, engine='openpyxl')

    def _required_columns(self):
        return ["Denumire comerciala"]

    def parse(self):
        
        self._df["ID"] = [f"RO_{i + 1}" for i in range(len(self._df))]
        
        self._df["properties"] = self._df.apply(lambda row: row.drop(
            ["ID", "Denumire comerciala"]).dropna().to_dict(), axis=1)
        
        # Select relevant columns
        self._df = self._df[["ID", "Denumire comerciala", "properties"]]
        self._df.rename(columns={
            "ID": "drug_code",
            "Denumire comerciala": "drug_name",
            "properties": "properties"
        }, inplace=True)
