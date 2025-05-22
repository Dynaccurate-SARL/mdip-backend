import chardet
import pandas as pd

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser


class US_Parser(PandasParser):
    def _open(self):
        encoding = chardet.detect(self._file)["encoding"]
        return pd.read_csv(
            self._file, delimiter="\t", encoding=encoding, on_bad_lines="skip"
        ).where(pd.notnull, None)

    def _required_columns(self):
        return ["DrugName"]

    def parse(self):
        self._df["ID"] = [f"US_{i + 1}" for i in range(len(self._df))]

        self._df["properties"] = self._df.apply(
            lambda row: row.drop(["ID", "DrugName"]).dropna().to_dict(), axis=1
        )

        # Select relevant columns
        self._df = self._df[["ID", "DrugName", "properties"]]
        self._df.rename(
            columns={
                "ID": "drug_code",
                "DrugName": "drug_name",
                "properties": "properties",
            },
            inplace=True,
        )
