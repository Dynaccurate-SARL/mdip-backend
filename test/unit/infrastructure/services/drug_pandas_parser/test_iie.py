import io
import pytest
import pandas as pd

from src.infrastructure.services.pandas_parser.drug.impl.iie import IE_Parser
from src.infrastructure.services.pandas_parser.drug.exc import (
    InvalidFileFormat)


def test_ie_open_and_validate_invalid_file():
    # Arrange
    mock_file = io.BytesIO(
        b"""
        <h:Products xmlns:h="https://assets.hpra.ie/products//xml/Human">
            <h:Product>
                <h:ID>1</h:ID>
                <h:Price>10.5</h:Price>
            </h:Product>
            <h:Product>
                <h:ID>2</h:ID>
                <h:Price>20.0</h:Price>
            </h:Product>
        </h:Products>
        """
    )

    # Act & Assert
    with pytest.raises(
            InvalidFileFormat,
            match="Missing required columns"):
        IE_Parser(mock_file)


def test_ie_parse_valid_data():
    # Arrange
    mock_file = io.BytesIO(
        b"""
        <h:Products xmlns:h="https://assets.hpra.ie/products//xml/Human">
            <h:Product>
                <h:ProductName>Attack 2</h:ProductName>
                <h:Extra>android</h:Extra>
            </h:Product>
            <h:Product>
                <h:ProductName>2 Mo. Battle</h:ProductName>
                <h:Extra>android</h:Extra>
            </h:Product>
        </h:Products>
        """
    )

    # Act
    parser = IE_Parser(mock_file)
    parser.parse()

    # Assert
    assert sorted(parser._df.columns) == [
        "drug_code", "drug_name", "properties"]
    assert parser._df.iloc[0]["drug_code"] == "IE_1"
    assert parser._df.iloc[0]["drug_name"] == "Attack 2"
    assert parser._df.iloc[0]["properties"] == {"Extra": "android"}
