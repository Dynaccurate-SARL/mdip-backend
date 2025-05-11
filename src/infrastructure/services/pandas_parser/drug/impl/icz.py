import chardet
import pandas as pd

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser


class CZ_Parser(PandasParser):
    def _open(self):
        encoding = chardet.detect(self._file)['encoding']
        return pd.read_csv(self._file, delimiter=';', encoding=encoding, dtype=str,
                           on_bad_lines='skip').where(pd.notnull, None)

    def _required_columns(self):
        return ["KOD_SUKL", "NAZEV"]

    def parse(self):
        self._df["properties"] = self._df.apply(lambda row: row.drop(
            ["KOD_SUKL", "NAZEV"]).dropna().to_dict(), axis=1)

        # Select relevant columns
        self._df = self._df[["KOD_SUKL", "NAZEV", "properties"]]
        self._df.rename(columns={
            "KOD_SUKL": "drug_code",
            "NAZEV": "drug_name",
            "properties": "properties"
        }, inplace=True)
