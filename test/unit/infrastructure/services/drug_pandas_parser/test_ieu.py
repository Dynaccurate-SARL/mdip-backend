import io
import pytest
import pandas as pd

from src.infrastructure.services.pandas_parser.drug.impl.ieu import EU_Parser
from src.infrastructure.services.pandas_parser.drug.exc import (
    InvalidFileFormat)


def test_open_and_validate_valid_file():
    # Arrange
    mock_file = io.BytesIO()
    valid_data = pd.DataFrame([
        ["0", "0", "0"],
        ["0", "0", "0"],
        ["0", "0", "0"],
        ["0", "0", "0"],
        ["ProductNumber", "ProductName", "Extra"],
        ["Drug 1", "Drug A", "test"],
        ["Drug 2", "Drug B", "test"],
        ["Drug 3", "Drug C", "test"]
    ])
    valid_data.columns = valid_data.iloc[0]
    valid_data = valid_data[1:]
    valid_data.to_excel(mock_file, index=False, engine='openpyxl')
    mock_file.seek(0)

    # Act & Assert
    EU_Parser(mock_file)


def test_open_and_validate_invalid_file():
    # Arrange
    mock_file = io.BytesIO()
    invalid_data = pd.DataFrame([
        ["0", "0", "0"],
        ["0", "0", "0"],
        ["0", "0", "0"],
    ])
    invalid_data.to_excel(mock_file, index=False, engine='openpyxl')
    mock_file.seek(0)

    # Act & Assert
    with pytest.raises(
            InvalidFileFormat,
            match="Invalid file format or missing required columns"):
        EU_Parser(mock_file)


def test_parse_valid_data():
    # Arrange
    mock_file = io.BytesIO()
    valid_data = pd.DataFrame([
        ["0", "0", "0"],
        ["0", "0", "0"],
        ["0", "0", "0"],
        ["0", "0", "0"],
        ["ProductNumber", "ProductName", "Extra"],
        ["Drug 1", "Drug A", "test"],
        ["Drug 2", "Drug B", "test"],
        ["Drug 3", "Drug C", "test"]
    ])
    valid_data.columns = valid_data.iloc[0]
    valid_data = valid_data[1:]
    valid_data.to_excel(mock_file, index=False, engine='openpyxl')
    mock_file.seek(0)

    # Act
    parser = EU_Parser(mock_file)
    parser.parse()

    # Assert
    assert list(parser._df.columns) == ["drug_code", "drug_name", "properties"]
    assert parser._df.iloc[0]["drug_code"] == "Drug 1"
    assert parser._df.iloc[0]["drug_name"] == "Drug A"
    assert parser._df.iloc[0]["properties"] == {"Extra": "test"}
