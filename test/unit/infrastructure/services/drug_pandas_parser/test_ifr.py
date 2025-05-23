import io
import pandas as pd

from src.infrastructure.services.pandas_parser.drug.impl.ifr import FR_Parser


def test_fr_parse_valid_data():
    # Arrange
    mock_file = io.BytesIO()
    valid_data = pd.DataFrame([
        ["A2", "0", "Attack 2", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
        ["2B", "0", "2 Mo. Battle", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0"],
    ])
    valid_data.to_csv(mock_file, sep="\t", index=False,
                      header=False, na_rep="")
    mock_file.seek(0)

    # Act
    parser = FR_Parser(mock_file)
    parser.parse()

    # Assert
    assert sorted(parser._df.columns) == [
        "drug_code", "drug_name", "properties"]
    assert parser._df.iloc[0]["drug_code"] == "A2"
    assert parser._df.iloc[0]["drug_name"] == "Attack 2"
