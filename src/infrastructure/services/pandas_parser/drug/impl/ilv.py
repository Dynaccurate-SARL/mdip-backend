import os
import zipfile
import tempfile
import pandas as pd

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser


class LV_Parser(PandasParser):
    def _open(self):
        temp_folder = tempfile.mkdtemp()
        with zipfile.ZipFile(self._file, "r") as zip_ref:
            zip_ref.extractall(temp_folder)

        drug_file = [f for f in zip_ref.namelist() if f.endswith(".xml")][0]
        return pd.read_xml(os.path.join(temp_folder, drug_file), xpath=".//product")

    def _required_columns(self):
        return ["product_id", "original_name"]

    def parse(self):
        self._df["properties"] = self._df.apply(
            lambda row: row.drop(["product_id", "original_name"]).dropna().to_dict(),
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
