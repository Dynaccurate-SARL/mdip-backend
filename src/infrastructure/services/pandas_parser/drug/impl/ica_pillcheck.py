import pandas as pd

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser


class CA_PillcheckParser(PandasParser):
    def _open(self):
        return pd.read_json(self._file)

    def _required_columns(self):
        return ["Generic Name"]

    def parse(self):
        # Rename the DataFrame columns
        self._df.rename(columns={
            "Generic Name": "drug_name",
        }, inplace=True)

        self._df["drug_code"] = self._df["drug_name"]
        self._df["properties"] = self._df.apply(lambda row: row.drop(
            ["drug_code", "drug_name"]).dropna().to_dict(), axis=1)

        self._df = self._df[["drug_code", "drug_name", "properties"]]
