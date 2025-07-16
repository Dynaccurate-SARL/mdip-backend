import pandas as pd

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser
from src.utils.file import detect_file_encoding


class SI_Parser(PandasParser):
    def _open(self):
        encoding = detect_file_encoding(self._file)
        return pd.read_csv(
            self._file, delimiter=";", 
            encoding=encoding, 
            on_bad_lines="skip",
            dtype=str
        ).where(pd.notnull, None)

    def _required_columns(self):
        return ["Nacionalna šifra ", "Poimenovanje zdravila"]

    def parse(self):

        self._df.columns = self._df.columns.str.strip()

        self._df["properties"] = self._df.apply(
            lambda row: row.drop(["Nacionalna šifra", "Poimenovanje zdravila"]).dropna().to_dict(), axis=1
        )

        # Select relevant columns
        self._df = self._df[["Nacionalna šifra", "Poimenovanje zdravila", "properties"]]
        self._df.rename(
            columns={
                "Nacionalna šifra": "drug_code",
                "Poimenovanje zdravila": "drug_name",
                "properties": "properties",
            },
            inplace=True,
        )

        self._df.dropna(subset=["drug_code", "drug_name"], inplace=True)
