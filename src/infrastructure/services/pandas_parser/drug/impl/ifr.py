import chardet
import pandas as pd

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser


class FR_Parser(PandasParser):
    def _open(self):
        encoding = chardet.detect(self._file.getvalue())["encoding"]
        df = pd.read_csv(
            self._file,
            delimiter="\t",
            encoding=encoding,
            on_bad_lines="skip",
            header=None,
        ).where(pd.notnull, None)

        # Reset the index
        df = df.reset_index(drop=True)

        # Assign your column names
        df.columns = [
            "CIS code",
            "CIP7 code",
            "Presentation title",
            "Admin status",
            "Marketing status",
            "Marketing declaration date",
            "CIP13 code",
            "Community approval",
            "Reimbursement rate(s)",
            "Drug price in euros",
            "description not specified",
            "description not specified",
            "Reimbursement indications",
        ]
        return df

    def _required_columns(self):
        return []

    def parse(self):
        # Strip whitespace from column names
        self._df.columns = self._df.columns.str.strip()

        self._df["properties"] = self._df.apply(
            lambda row: row.drop(["CIS code", "Presentation title"]).dropna().to_dict(),
            axis=1,
        )

        # Select relevant columns
        self._df = self._df[["CIS code", "Presentation title", "properties"]]
        self._df.rename(
            columns={
                "CIS code": "drug_code",
                "Presentation title": "drug_name",
                "properties": "properties",
            },
            inplace=True,
        )

        self._df.dropna(subset=["drug_code", "drug_name"], inplace=True)
