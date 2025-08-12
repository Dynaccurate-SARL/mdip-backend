import io
import pytest
import pandas as pd

from src.infrastructure.services.pandas_parser.drug.impl.ilt import LT_Parser
from src.infrastructure.services.pandas_parser.drug.exc import (
    InvalidFileFormat)


def test_lt_open_and_validate_invalid_file():
    # Arrange
    mock_file = io.BytesIO()
    invalid_data = pd.DataFrame([
        {"Extended": "2", "Name": "A"},
        {"Extended": "1", "Name": "A"},
    ])
    invalid_data.to_csv(mock_file, sep=";", index=False)
    mock_file.seek(0)

    # Act & Assert
    with pytest.raises(
            InvalidFileFormat,
            match="Missing required columns"):
        LT_Parser(mock_file)


def test_lt_parse_valid_data():
    # Arrange
    mock_file = io.BytesIO()
    valid_data = pd.DataFrame([
        {"Preparato (sugalvotas) pavadinimas": "Attack 2", "Extra": "android"},
        {"Preparato (sugalvotas) pavadinimas": "2 Mo. Battle", "Extra": "android"},
    ])
    valid_data.to_csv(mock_file, sep=";", index=False)
    mock_file.seek(0)

    # Act
    parser = LT_Parser(mock_file)
    parser.parse()

    # Assert
    assert sorted(parser._df.columns) == [
        "drug_code", "drug_name", "properties"]
    assert parser._df.iloc[0]["drug_code"] == "LT_1"
    assert parser._df.iloc[0]["drug_name"] == "Attack 2"
    assert parser._df.iloc[0]["properties"] == {"Extra": "android"}
