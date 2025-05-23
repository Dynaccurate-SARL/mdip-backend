import pandas as pd

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser


class HR_Parser(PandasParser):
    def _open(self):
        return pd.read_json(self._file)

    def _required_columns(self):
        return ["DRUG_CODE", "BRAND_NAME"]

    def parse(self):
        # Rename the DataFrame columns
        self._df.rename(
            columns={
                "DRUG_CODE": "drug_code",
                "BRAND_NAME": "drug_name",
            },
            inplace=True,
        )

        self._df["properties"] = self._df.apply(
            lambda row: row.drop(["drug_code", "drug_name"]).to_dict(), axis=1
        )

        self._df = self._df[["drug_code", "drug_name", "properties"]]
