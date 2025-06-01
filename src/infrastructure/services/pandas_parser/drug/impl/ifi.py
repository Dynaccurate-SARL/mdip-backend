import pandas as pd
import xml.etree.ElementTree as ET

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser


class FI_Parser(PandasParser):
    def _open(self):
        tree = ET.parse(self._file)
        root = tree.getroot()
        records = []
        for product in root.findall(".//Laakevalmiste"):
            record = {}
            record["id"] = product.attrib.get("id")
            for child in product:
                tag = child.tag
                if tag == "ATC-koodi":
                    record["ATC-koodi"] = child.attrib.get("id")
                elif tag == "Laakemuoto":
                    record["Laakemuoto"] = child.attrib.get("value")
                elif tag == "Myyntilupa":
                    myyntilupa = {}
                    for subchild in child:
                        myyntilupa[subchild.tag] = subchild.text
                    record["Myyntilupa"] = myyntilupa
                else:
                    record[tag] = child.text
            records.append(record)
        

        return pd.DataFrame(records)

    def _required_columns(self):
        return ["id", "Kauppanimi"]

    def parse(self):

        # Convert to Dict format for properties
        self._df["properties"] = self._df.apply(
            lambda row: row.drop(["id", "Kauppanimi"]).dropna().to_dict(), axis=1
        )

        # Select relevant columns
        self._df = self._df[["id", "Kauppanimi", "properties"]]
        self._df.rename(
            columns={
                "id": "drug_code",
                "Kauppanimi": "drug_name",
                "properties": "properties",
            },
            inplace=True,
        )

        self._df = self._df.dropna()
