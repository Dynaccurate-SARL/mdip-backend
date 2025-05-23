import io
import pytest
import pandas as pd

from src.infrastructure.services.pandas_parser.drug.impl.iuk import UK_Parser
from src.infrastructure.services.pandas_parser.drug.exc import (
    InvalidFileFormat)


def test_uk_open_and_validate_invalid_file():
    # Arrange
    mock_file = io.BytesIO()
    invalid_data = pd.DataFrame([
        ["A", "B"],
        ["Attack 2", "android"],
        ["2 Mo. Battle", "android"],
    ])
    invalid_data.to_csv(mock_file, sep=",", index=False, header=False)
    mock_file.seek(0)

    # Act & Assert
    with pytest.raises(
            InvalidFileFormat,
            match="Missing required columns"):
        UK_Parser(mock_file)


def test_uk_parse_valid_data():
    # Arrange
    mock_file = io.BytesIO()
    valid_data = pd.DataFrame([
        ["VMP_PRODUCT_NAME", "Extra"],
        ["Attack 2", "android"],
        ["2 Mo. Battle", "android"],
    ])
    valid_data.to_csv(mock_file, sep=",", index=False, header=False)
    mock_file.seek(0)

    # Act
    parser = UK_Parser(mock_file)
    parser.parse()

    # Assert
    assert sorted(parser._df.columns) == [
        "drug_code", "drug_name", "properties"]
    assert parser._df.iloc[0]["drug_code"] == "UK_1"
    assert parser._df.iloc[0]["drug_name"] == "Attack 2"
    assert parser._df.iloc[0]["properties"] == {"Extra": "android"}
