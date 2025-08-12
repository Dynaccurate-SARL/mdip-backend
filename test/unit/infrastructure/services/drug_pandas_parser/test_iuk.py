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
        {"Extended": "2", "Name": "A"},
        {"Extended": "2", "Name": "B"},
    ])
    invalid_data.to_json(mock_file)
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
        {"VMP ID": "A2", "Name": "Attack 2", "Extra": "android"},
        {"VMP ID": "2B", "Name": "2 Mo. Battle", "Extra": "android"},
    ])
    valid_data.to_json(mock_file)
    mock_file.seek(0)

    # Act
    parser = UK_Parser(mock_file)
    parser.parse()

    # Assert
    assert sorted(parser._df.columns) == [
        "drug_code", "drug_name", "properties"]
    assert parser._df.iloc[0]["drug_code"] == "A2"
    assert parser._df.iloc[0]["drug_name"] == "Attack 2"
    assert parser._df.iloc[0]["properties"] == {"Extra": "android"}
