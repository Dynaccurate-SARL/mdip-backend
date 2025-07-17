import pandas as pd

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser


class UK_Parser(PandasParser):
    def _open(self):
        return pd.read_json(
            self._file, dtype=str
        ).where(pd.notnull, None)

    def _required_columns(self):
        return ["VMP ID", "Name"]

    def parse(self):
        self._df["properties"] = self._df.apply(
            lambda row: row.drop(["VMP ID", "Name"]).dropna().to_dict(), axis=1
        )

        self._df = self._df[["VMP ID", "Name", "properties"]]
        self._df.rename(
            columns={
                "VMP ID": "drug_code",
                "Name": "drug_name",
                "properties": "properties",
            },
            inplace=True,
        )

        self._df.dropna()
