import chardet
import pandas as pd

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser


class HU_Parser(PandasParser):
    def _open(self):
        encoding = chardet.detect(self._file.getvalue())["encoding"]
        return pd.read_csv(
            self._file, delimiter=";", encoding=encoding, on_bad_lines="skip", dtype=str
        ).where(pd.notnull, None)

    def _required_columns(self):
        return [" Név"]

    def parse(self):
        self._df["ID"] = [f"HU_{i + 1}" for i in range(len(self._df))]

        self._df.columns = self._df.columns.str.strip()

        self._df["properties"] = self._df.apply(
            lambda row: row.drop(["ID", "Név"]).dropna().to_dict(), axis=1
        )

        # Select relevant columns
        self._df = self._df[["ID", "Név", "properties"]]
        self._df.rename(
            columns={"ID": "drug_code", "Név": "drug_name", "properties": "properties"},
            inplace=True,
        )

        self._df = self._df.dropna()
