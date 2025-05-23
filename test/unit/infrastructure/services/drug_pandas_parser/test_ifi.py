import io
import pytest
import pandas as pd

from src.infrastructure.services.pandas_parser.drug.impl.ifi import FI_Parser
from src.infrastructure.services.pandas_parser.drug.exc import (
    InvalidFileFormat)


def test_fi_open_and_validate_invalid_file():
    # Arrange
    mock_file = io.BytesIO(
        b"""
        <Data>
            <Laakevalmiste>
                <Nimi>Paracetamol</Nimi>
                <Annos>500mg</Annos>
            </Laakevalmiste>
            <Laakevalmiste>
                <Nimi>Ibuprofeeni</Nimi>
                <Annos>200mg</Annos>
            </Laakevalmiste>
        </Data>
        """
    )

    # Act & Assert
    with pytest.raises(
            InvalidFileFormat,
            match="Missing required columns"):
        FI_Parser(mock_file)


def test_fi_parse_valid_data():
    # Arrange
    mock_file = io.BytesIO(
        b"""
        <Data>
            <Laakevalmiste>
                <id>A2</id>
                <Kauppanimi>Attack 2</Kauppanimi>
                <Extra>android</Extra>
            </Laakevalmiste>
            <Laakevalmiste>
                <id>2B</id>
                <Kauppanimi>2 Mo. Battle</Kauppanimi>
                <Extra>android</Extra>
            </Laakevalmiste>
        </Data>
        """
    )

    # Act
    parser = FI_Parser(mock_file)
    parser.parse()

    # Assert
    assert sorted(parser._df.columns) == [
        "drug_code", "drug_name", "properties"]
    assert parser._df.iloc[0]["drug_code"] == "A2"
    assert parser._df.iloc[0]["drug_name"] == "Attack 2"
    assert parser._df.iloc[0]["properties"] == {"Extra": "android"}
