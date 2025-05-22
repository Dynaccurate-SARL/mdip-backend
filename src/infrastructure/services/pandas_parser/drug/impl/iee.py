import chardet
import pandas as pd

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser


class EE_Parser(PandasParser):
    def _open(self):
        encoding = chardet.detect(self._file)["encoding"]
        return pd.read_csv(
            self._file, delimiter=";", header=1, encoding=encoding, on_bad_lines="skip"
        ).where(pd.notnull, None)

    def _required_columns(self):
        return ["Name of medicinal product"]

    def parse(self):
        self._df["ID"] = [f"EE_{i + 1}" for i in range(len(self._df))]

        self._df["properties"] = self._df.apply(
            lambda row: row.drop(["ID", "Name of medicinal product"])
            .dropna()
            .to_dict(),
            axis=1,
        )

        # Select relevant columns
        self._df = self._df[["ID", "Name of medicinal product", "properties"]]
        self._df.rename(
            columns={
                "ID": "drug_code",
                "Name of medicinal product": "drug_name",
                "properties": "properties",
            },
            inplace=True,
        )

        self._df.dropna(subset=["drug_code", "drug_name"], inplace=True)
