import io
import zipfile
import pandas as pd

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser


def _extract_xml_from_zip(zip_bytesio: io.BytesIO) -> io.BytesIO:
    zip_bytesio.seek(0)
    with zipfile.ZipFile(zip_bytesio, "r") as zipf:
        for name in zipf.namelist():
            if name.lower().endswith(".xml"):
                return io.BytesIO(zipf.read(name))
        raise FileNotFoundError("No XML file found in ZIP.")


class LV_Parser(PandasParser):
    def _open(self):
        self._file = _extract_xml_from_zip(self._file)
        return pd.read_xml(self._file, xpath=".//product")

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
