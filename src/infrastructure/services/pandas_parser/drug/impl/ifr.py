import pandas as pd

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser
from src.utils.file import detect_file_encoding


class FR_Parser(PandasParser):
    def _open(self):
        encoding = detect_file_encoding(self._file)
        df = pd.read_csv(
            self._file,
            delimiter="\t",
            encoding=encoding,
            on_bad_lines="skip",
            header=None,
            dtype=str,
        ).where(pd.notnull, None)

        # Reset the index
        df = df.reset_index(drop=True)

        # Assign your column names
        df.columns = [
            "CIS code",
            "ATC code",
            "Drug name",
            "BDPM link",
        ]
        return df

    def _required_columns(self):
        return []

    def parse(self):

        self._df["properties"] = self._df.apply(
            lambda row: row.drop(["CIS code", "Drug name"]).dropna().to_dict(),
            axis=1,
        )

        # Select relevant columns
        self._df = self._df[["CIS code", "Drug name", "properties"]]
        self._df.rename(
            columns={
                "CIS code": "drug_code",
                "Drug name": "drug_name",
                "properties": "properties",
            },
            inplace=True,
        )

        self._df = self._df.dropna()
