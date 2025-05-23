import io
import pytest
import pandas as pd

from src.infrastructure.services.pandas_parser.drug.impl.ilu import LU_Parser
from src.infrastructure.services.pandas_parser.drug.exc import (
    InvalidFileFormat)


def test_lu_open_and_validate_invalid_file():
    # Arrange
    mock_file = io.BytesIO()
    invalid_data = pd.DataFrame([
        {"Extended": "2", "Name": "A"},
        {"Extended": "1", "Name": "A"},
    ])
    invalid_data.to_excel(mock_file, index=False, engine="openpyxl")
    mock_file.seek(0)

    # Act & Assert
    with pytest.raises(
            InvalidFileFormat,
            match="Missing required columns"):
        LU_Parser(mock_file)


def test_lu_parse_valid_data():
    # Arrange
    mock_file = io.BytesIO()
    valid_data = pd.DataFrame([
        ["0", "0", "0"],
        ["0", "0", "0"],
        ["Nr. AMM", "Dénomination", "Extra"],
        ["A2", "Attack 2", "android"],
        ["2B", "2 Mo. Battle", "android"],
    ])
    valid_data.columns = valid_data.iloc[0]
    valid_data = valid_data[1:]
    valid_data.to_excel(mock_file, index=False, engine="openpyxl")
    mock_file.seek(0)

    # Act
    parser = LU_Parser(mock_file)
    parser.parse()

    # Assert
    assert sorted(parser._df.columns) == [
        "drug_code", "drug_name", "properties"]
    assert parser._df.iloc[0]["drug_code"] == "A2"
    assert parser._df.iloc[0]["drug_name"] == "Attack 2"
    assert parser._df.iloc[0]["properties"] == {"Extra": "android"}
