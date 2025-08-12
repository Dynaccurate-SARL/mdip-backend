import io
import xlwt
import pytest
import pandas as pd
from typing import List

from src.infrastructure.services.pandas_parser.drug.impl.isk import SK_Parser
from src.infrastructure.services.pandas_parser.drug.exc import (
    InvalidFileFormat)


def create_mock_file(data: List[List[str]]) -> io.BytesIO:
    workbook = xlwt.Workbook()
    sheet = workbook.add_sheet('MySheet')

    for row_index, row in enumerate(data):
        for col_index, cell_data in enumerate(row):
            sheet.write(row_index, col_index, cell_data)
    mock_file = io.BytesIO()
    workbook.save(mock_file)
    return mock_file


def test_sk_open_and_validate_invalid_file():
    # Arrange
    mock_file = create_mock_file([
        ["0", "0", "0"],
        ["0", "0", "0"],
        ["0", "0", "0"],
    ])

    # Act & Assert
    with pytest.raises(
            InvalidFileFormat,
            match="Missing required columns"):
        SK_Parser(mock_file)


def test_sk_parse_valid_data():
    # Arrange
    mock_file = create_mock_file([
        ["ŠÚKL kód", "Názov", "Extra"],
        ["A2", "Attack 2", "android"],
        ["2B", "2 Mo. Battle", "android"]
    ])

    # Act
    parser = SK_Parser(mock_file)
    parser.parse()

    # Assert
    assert sorted(parser._df.columns) == [
        "drug_code", "drug_name", "properties"]
    assert parser._df.iloc[0]["drug_code"] == "A2"
    assert parser._df.iloc[0]["drug_name"] == "Attack 2"
    assert parser._df.iloc[0]["properties"] == {"Extra": "android"}
