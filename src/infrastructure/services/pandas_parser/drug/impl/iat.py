import chardet
import pandas as pd

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser


class AT_Parser(PandasParser):
    def _open(self):
        return pd.read_excel(
            self._file,
            engine="openpyxl",
            sheet_name="Search results",
        ).where(pd.notnull, None)

    def _required_columns(self):
        return ["Name"]

    def parse(self):
        # Strip whitespace from column names
        self._df.columns = self._df.columns.str.strip()

        self._df["properties"] = self._df.apply(
            lambda row: row.drop(["Name"]).dropna().to_dict(), axis=1
        )

        # Generate ID column
        self._df["ID"] = [f"AT_{i + 1}" for i in range(len(self._df))]

        # Select relevant columns
        self._df = self._df[["Name", "ID", "properties"]]
        self._df.rename(
            columns={
                "ID": "drug_code",
                "Name": "drug_name",
                "properties": "properties",
            },
            inplace=True,
        )
