import pandas as pd
import xml.etree.ElementTree as ET

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser


class IE_Parser(PandasParser):
    def _open(self):
        tree = ET.parse(self._file)
        root = tree.getroot()
        ns = {"h": "https://assets.hpra.ie/products//xml/Human"}

        records = []
        for product in root.findall(".//h:Product", ns):
            record = {}
            for child in product:
                tag = child.tag.split("}", 1)[-1]
                # Check if this field has nested elements
                if len(child) > 0:
                    values = [c.text for c in child if c.text is not None]
                    record[tag] = values
                else:
                    record[tag] = child.text
            records.append(record)

        return pd.DataFrame(records)

    def _required_columns(self):
        return ["ProductName"]

    def parse(self):

        self._df["ID"] = [f"IE_{i + 1}" for i in range(len(self._df))]

        # Convert to Dict format for properties
        self._df["properties"] = self._df.apply(
            lambda row: row.drop(["ID", "ProductName"]).dropna().to_dict(), axis=1
        )

        # Select relevant columns
        self._df = self._df[["ID", "ProductName", "properties"]]
        self._df.rename(
            columns={
                "ID": "drug_code",
                "ProductName": "drug_name",
                "properties": "properties",
            },
            inplace=True,
        )

        self._df = self._df.dropna()
