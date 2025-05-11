import pandas as pd

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser


class CA_PillcheckParser(PandasParser):
    def _open(self):
        return pd.read_excel(self._file, engine='openpyxl')

    def _required_columns(self):
        return ["Generic Name"]

    def parse(self):
        
        self._df.drop(columns=["Unnamed: 6"], inplace=True)

        self._df["ID"] = [f"CAPC_{i + 1}" for i in range(len(self._df))]
        
        self._df["properties"] = self._df.apply(lambda row: row.drop(
            ["ID", "Generic Name"]).dropna().to_dict(), axis=1)

        self._df = self._df[["ID", "Generic Name", "properties"]]
        self._df.rename(columns={
            "ID": "drug_code",
            "Generic Name": "drug_name",
            "properties": "properties"
        }, inplace=True)