import pandas as pd

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser


class MT_Parser(PandasParser):
    def _open(self):
        return pd.read_excel(self._file, engine='openpyxl')

    def _required_columns(self):
        return ["[Medicine Name]"]

    def parse(self):

        self._df["ID"] = [f"MT_{i + 1}" for i in range(len(self._df))]

        self._df["properties"] = self._df.apply(lambda row: row.drop(
            ["ID", "[Medicine Name]"]).dropna().to_dict(), axis=1)

        self._df = self._df[["ID", "[Medicine Name]", "properties"]]
        self._df.rename(columns={
            "ID": "drug_code",
            "[Medicine Name]": "drug_name",
            "properties": "properties"
        }, inplace=True)
