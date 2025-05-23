import pandas as pd

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser


class IE_Parser(PandasParser):
    def _open(self):
        return pd.read_xml(
            self._file,
            xpath=".//h:Product",
            namespaces={"h": "https://assets.hpra.ie/products//xml/Human"},
        )

    def _required_columns(self):
        return ["DrugIDPK", "ProductName"]

    def parse(self):
        # Strip whitespace from column names
        self._df.columns = self._df.columns.str.strip()

        # Convert to Dict format for properties
        self._df["properties"] = self._df.apply(
            lambda row: row.drop(["DrugIDPK", "ProductName"]).dropna().to_dict(), axis=1
        )

        # Select relevant columns
        self._df = self._df[["DrugIDPK", "ProductName", "properties"]]
        self._df.rename(
            columns={
                "DrugIDPK": "drug_code",
                "ProductName": "drug_name",
                "properties": "properties",
            },
            inplace=True,
        )
