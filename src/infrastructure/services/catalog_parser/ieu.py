import io
import pandas as pd

from src.infrastructure.services.catalog_parser.contract import Parser


class EU_Parser(Parser):
    def _open_and_validate(self):
        try:
            self._df = pd.read_excel(self._file, engine='openpyxl', skiprows=4)

            required_columns = ["ProductNumber", "ProductName"]
            if not all(col in self._df.columns for col in required_columns):
                raise ValueError()
        except:
            raise ValueError("Invalid file format or missing required columns")

    def parse(self):
        # Strip whitespace from column names
        self._df.columns = self._df.columns.str.strip()

        # Convert to JSON-like format for properties
        self._df["properties"] = self._df.apply(lambda row: row.drop(
            ["ProductNumber", "ProductName"]).dropna().to_dict(), axis=1)

        # Select relevant columns
        self._df = self._df[["ProductNumber", "ProductName", "properties"]]
        self._df.rename(columns={
            "ProductNumber": "drug_code",
            "ProductName": "drug_name",
            "properties": "properties"
        }, inplace=True)
