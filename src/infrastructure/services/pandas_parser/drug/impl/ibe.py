import chardet
import pandas as pd

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser


class BE_Parser(PandasParser):
    def _open(self):
        encoding = chardet.detect(self._file.getvalue())["encoding"]
        return pd.read_csv(
            self._file, delimiter=";", encoding=encoding, on_bad_lines="skip"
        ).where(pd.notnull, None)

    def _required_columns(self):
        return ["CTI Extended", "Name"]

    def parse(self):
        # Strip whitespace from column names
        self._df.columns = self._df.columns.str.strip()

        self._df["properties"] = self._df.apply(
            lambda row: row.drop(["CTI Extended", "Name"]).dropna().to_dict(), axis=1
        )

        # Select relevant columns
        self._df = self._df[["CTI Extended", "Name", "properties"]]
        self._df.rename(
            columns={
                "CTI Extended": "drug_code",
                "Name": "drug_name",
                "properties": "properties",
            },
            inplace=True,
        )

        self._df.dropna(subset=["drug_code", "drug_name"], inplace=True)
