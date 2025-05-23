import io
import pytest
import pandas as pd

from src.infrastructure.services.pandas_parser.drug.impl.ipl import PL_Parser
from src.infrastructure.services.pandas_parser.drug.exc import (
    InvalidFileFormat)


def test_pl_open_and_validate_invalid_file():
    # Arrange
    mock_file = io.BytesIO()
    invalid_data = pd.DataFrame([
        ["A", "B"],
        ["Attack 2", "android"],
        ["2 Mo. Battle", "android"],
    ])
    invalid_data.to_csv(mock_file, sep=";", index=False, header=False)
    mock_file.seek(0)

    # Act & Assert
    with pytest.raises(
            InvalidFileFormat,
            match="Missing required columns"):
        PL_Parser(mock_file)


def test_pl_parse_valid_data():
    # Arrange
    mock_file = io.BytesIO()
    valid_data = pd.DataFrame([
        ["Identyfikator Produktu Leczniczego",
            "Nazwa Produktu Leczniczego", "Extra"],
        ["A2", "Attack 2", "android"],
        ["2B", "2 Mo. Battle", "android"],
    ])
    valid_data.to_csv(mock_file, sep=";", index=False, header=False)
    mock_file.seek(0)

    # Act
    parser = PL_Parser(mock_file)
    parser.parse()

    # Assert
    assert sorted(parser._df.columns) == [
        "drug_code", "drug_name", "properties"]
    assert parser._df.iloc[0]["drug_code"] == "A2"
    assert parser._df.iloc[0]["drug_name"] == "Attack 2"
    assert parser._df.iloc[0]["properties"] == {"Extra": "android"}
