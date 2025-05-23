import pandas as pd

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser


class FI_Parser(PandasParser):
    def _open(self):
        return pd.read_xml(self._file, xpath=".//Laakevalmiste").dropna(
            axis=1, how="all"
        )

    def _required_columns(self):
        return ["id", "Kauppanimi"]

    def parse(self):
        # Strip whitespace from column names
        self._df.columns = self._df.columns.str.strip()

        # Convert to Dict format for properties
        self._df["properties"] = self._df.apply(
            lambda row: row.drop(["id", "Kauppanimi"]).dropna().to_dict(), axis=1
        )

        # Select relevant columns
        self._df = self._df[["id", "Kauppanimi", "properties"]]
        self._df.rename(
            columns={
                "id": "drug_code",
                "Kauppanimi": "drug_name",
                "properties": "properties",
            },
            inplace=True,
        )
