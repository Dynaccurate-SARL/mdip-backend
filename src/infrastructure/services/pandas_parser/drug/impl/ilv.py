import chardet
import pandas as pd

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser


class LV_Parser(PandasParser):
    def _open(self):
        encoding = chardet.detect(self._file.getvalue())["encoding"]
        return pd.read_json(
            self._file, dtype=str, encoding=encoding
        ).replace("", pd.NA)

    def _required_columns(self):
        return ["product_id", "original_name"]

    def parse(self):
        self._df["properties"] = self._df.apply(
            lambda row: row.drop(
                ["product_id", "original_name"]).dropna().to_dict(),
            axis=1,
        )

        # Select relevant columns
        self._df = self._df[["product_id", "original_name", "properties"]]
        self._df.rename(
            columns={
                "product_id": "drug_code",
                "original_name": "drug_name",
                "properties": "properties",
            },
            inplace=True,
        )

        self._df = self._df.dropna()
