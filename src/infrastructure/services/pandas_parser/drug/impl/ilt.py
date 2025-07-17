import pandas as pd

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser
from src.utils.file import detect_file_encoding


class LT_Parser(PandasParser):
    def _open(self):
        encoding = detect_file_encoding(self._file)
        return pd.read_csv(
            self._file, delimiter=";", 
            encoding=encoding, 
            on_bad_lines="skip",
            dtype=str
        ).where(pd.notnull, None)

    def _required_columns(self):
        return ["Preparato (sugalvotas) pavadinimas"]

    def parse(self): 
        self._df["ID"] = [f"LT_{i + 1}" for i in range(len(self._df))]

        self._df["properties"] = self._df.apply(
            lambda row: row.drop(["ID", "Preparato (sugalvotas) pavadinimas"]).dropna().to_dict(), axis=1
        )

        # Select relevant columns
        self._df = self._df[["ID", "Preparato (sugalvotas) pavadinimas", "properties"]]
        self._df.rename(
            columns={
                "ID": "drug_code",
                "Preparato (sugalvotas) pavadinimas": "drug_name",
                "properties": "properties",
            },
            inplace=True,
        )

        self._df.dropna(subset=["drug_code", "drug_name"], inplace=True)
