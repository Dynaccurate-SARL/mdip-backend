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
        <Root>
            <Laakevalmisteet>
                <Laakevalmiste id="123">
                    <Kauppanimi>Paracetamol</Kauppanimi>
                    <ATC-koodi id="N02BE01"/>
                    <Laakemuoto value="Tabletti"/>
                    <Myyntilupa>
                        <Myontipaiva>2020-01-01</Myontipaiva>
                        <LuvanHaltija>Pharma Oy</LuvanHaltija>
                    </Myyntilupa>
                </Laakevalmiste>
                <Laakevalmiste id="456">
                    <Kauppanimi>Ibuprofeeni</Kauppanimi>
                    <ATC-koodi id="M01AE01"/>
                    <Laakemuoto value="Tabletti"/>
                    <Myyntilupa>
                        <Myontipaiva>2019-05-10</Myontipaiva>
                        <LuvanHaltija>MedCo</LuvanHaltija>
                    </Myyntilupa>
                </Laakevalmiste>
            </Laakevalmisteet>
        </Root>
        """
    )

    # Act
    parser = FI_Parser(mock_file)
    parser.parse()

    # Assert
    assert sorted(parser._df.columns) == [
        "drug_code", "drug_name", "properties"]
    assert parser._df.iloc[0]["drug_code"] == "123"
    assert parser._df.iloc[0]["drug_name"] == "Paracetamol"
    assert parser._df.iloc[0]["properties"] == {
        'ATC-koodi': 'N02BE01',
        'Laakemuoto': 'Tabletti',
        'Myyntilupa': {
            'LuvanHaltija': 'Pharma Oy',
            'Myontipaiva': '2020-01-01'
        }
    }
