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
        self._dt.columns = self._dt.columns.str.strip()

        # Convert to Dict format for properties
        self._dt["properties"] = self._dt.apply(
            lambda row: row.drop(["id", "Kauppanimi"]).dropna().to_dict(), axis=1
        )

        # Select relevant columns
        self._dt = self._dt[["id", "Kauppanimi", "properties"]]
        self._dt.rename(
            columns={
                "id": "drug_code",
                "Kauppanimi": "drug_name",
                "properties": "properties",
            },
            inplace=True,
        )
