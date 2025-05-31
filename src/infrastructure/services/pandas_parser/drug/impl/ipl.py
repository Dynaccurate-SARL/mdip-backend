import chardet
import pandas as pd

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser


class PL_Parser(PandasParser):
    def _open(self):
        encoding = chardet.detect(self._file.getvalue())["encoding"]
        return pd.read_csv(
            self._file, delimiter=";", encoding=encoding, on_bad_lines="skip", dtype=str
        ).where(pd.notnull, None)

    def _required_columns(self):
        return ["Identyfikator Produktu Leczniczego", "Nazwa Produktu Leczniczego"]

    def parse(self):
        # Mapping of Polish to English column names
        column_mapping = {
            "Identyfikator Produktu Leczniczego": "drug_code",
            "Nazwa Produktu Leczniczego": "drug_name",
        }

        self._df["properties"] = self._df.apply(
            lambda row: row.drop(
                ["Identyfikator Produktu Leczniczego", "Nazwa Produktu Leczniczego"]
            )
            .dropna()
            .to_dict(),
            axis=1,
        )

        # Rename the DataFrame columns
        self._df.rename(columns=column_mapping, inplace=True)
        self._df = self._df[["drug_code", "drug_name", "properties"]]

        self._df.dropna()
