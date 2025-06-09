import io
from numpy import dtype
import pandas as pd

from src.infrastructure.services.pandas_parser.drug.impl.ifr import FR_Parser


def test_fr_parse_valid_data():
    # Arrange
    mock_file = io.BytesIO()
    valid_data = pd.DataFrame([
        ["A2", "1", "Attack 2", "A"],
        ["2B", "2", "2 Mo. Battle", "B"],
    ])
    valid_data.to_csv(mock_file, sep='\t', index=False, 
                      header=False, encoding='utf-8')
    mock_file.seek(0)

    # Act
    parser = FR_Parser(mock_file)
    parser.parse()

    # Assert
    assert sorted(parser._df.columns) == [
        "drug_code", "drug_name", "properties"]
    assert parser._df.iloc[0]["drug_code"] == "A2"
    assert parser._df.iloc[0]["drug_name"] == "Attack 2"
