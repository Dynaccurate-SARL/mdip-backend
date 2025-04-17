import chardet
import pandas as pd

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser


class ATC_Parser(PandasParser):
    def _open(self):
        encoding = chardet.detect(self._file)['encoding']
        return pd.read_csv(self._file, delimiter=',', encoding=encoding,
                           on_bad_lines='skip').where(pd.notnull, None)

    def _required_columns(self):
        return ["ATC code", "ATC level name"]

    def parse(self):
        # Strip whitespace from column names
        self._df.columns = self._df.columns.str.strip()

        self._df["properties"] = self._df.apply(lambda row: row.drop(
            ["ATC code", "ATC level name"]).dropna().to_dict(), axis=1)

        # Select relevant columns
        self._df = self._df[["ATC code", "ATC level name", "properties"]]
        self._df.rename(columns={
            "ATC code": "code",
            "ATC level name": "name",
            "properties": "properties"
        }, inplace=True)
