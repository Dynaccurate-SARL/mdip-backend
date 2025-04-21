import pandas as pd

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser


class UK_Parser(PandasParser):
    def _open(self):
        return pd.read_excel(self._file, engine='openpyxl')

    def _required_columns(self):
        return ["VMP_SNOMED_CODE", "VMP_PRODUCT_NAME"]

    def parse(self):
        # Strip whitespace from column names
        self._df.columns = self._df.columns.str.strip()

        self._df["properties"] = self._df.apply(lambda row: row.drop(
            ["VMP_SNOMED_CODE", "VMP_PRODUCT_NAME"]).dropna().to_dict(), axis=1)

        # Select relevant columns
        self._df = self._df[["VMP_SNOMED_CODE",
                             "VMP_PRODUCT_NAME", "properties"]]
        self._df.rename(columns={
            "VMP_SNOMED_CODE": "code",
            "VMP_PRODUCT_NAME": "drug_name",
            "properties": "properties"
        }, inplace=True)
