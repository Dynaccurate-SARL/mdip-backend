import pandas as pd

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser
from src.utils.file import detect_file_encoding


class IT_Parser(PandasParser):
    def _open(self):
        encoding = detect_file_encoding(self._file)
        return pd.read_csv(
            self._file, delimiter=";", 
            encoding=encoding, 
            on_bad_lines="skip",
            dtype=str
        ).where(pd.notnull, None)

    def _required_columns(self):
        return ["codice_aic", "denominazione"]

    def parse(self):

        self._df["properties"] = self._df.apply(
            lambda row: row.drop(["codice_aic", "denominazione"]).dropna().to_dict(), axis=1
        )

        # Select relevant columns
        self._df = self._df[["codice_aic", "denominazione", "properties"]]
        self._df.rename(
            columns={
                "codice_aic": "drug_code",
                "denominazione": "drug_name",
                "properties": "properties",
            },
            inplace=True,
        )

        self._df.dropna(subset=["drug_code", "drug_name"], inplace=True)
