import io
import pytest
import pandas as pd

from src.infrastructure.services.pandas_parser.drug.impl.isi import SI_Parser
from src.infrastructure.services.pandas_parser.drug.exc import (
    InvalidFileFormat)


def test_cz_open_and_validate_invalid_file():
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
        SI_Parser(mock_file)


def test_cz_parse_valid_data():
    # Arrange
    mock_file = io.BytesIO()
    valid_data = pd.DataFrame([
        {"Nacionalna šifra ": "A2",
            "Poimenovanje zdravila": "Attack 2", "Extra": "android"},
        {"Nacionalna šifra ": "2B",
            "Poimenovanje zdravila": "2 Mo. Battle", "Extra": "android"},
    ])
    csv_str = valid_data.to_csv(sep=";", index=False)
    mock_file.write('\ufeff'.encode('utf-8'))
    mock_file.write(csv_str.encode('utf-8'))
    mock_file.seek(0)

    # Act
    parser = SI_Parser(mock_file)
    parser.parse()

    # Assert
    assert sorted(parser._df.columns) == [
        "drug_code", "drug_name", "properties"]
    assert parser._df.iloc[0]["drug_code"] == "A2"
    assert parser._df.iloc[0]["drug_name"] == "Attack 2"
    assert parser._df.iloc[0]["properties"] == {"Extra": "android"}
