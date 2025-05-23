import io
import pytest
import zipfile
import pandas as pd

from src.infrastructure.services.pandas_parser.drug.impl.ilv import (
    LV_Parser, _extract_xml_from_zip)
from src.infrastructure.services.pandas_parser.drug.exc import (
    InvalidFileFormat)


def _zip_bytesio_file(input_bytesio: io.BytesIO) -> io.BytesIO:
    input_bytesio.seek(0)
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr("file.xml", input_bytesio.read())
    zip_buffer.seek(0)
    return zip_buffer


def test_lv_open_and_validate_invalid_file():
    # Arrange
    mock_file = io.BytesIO(
        b"""
        <products>
            <product>
                <id>1</id>
                <name>Produto A</name>
                <price>10.5</price>
            </product>
            <product>
                <id>2</id>
                <name>Produto B</name>
                <price>20.0</price>
            </product>
        </products>
        """
    )

    # Act & Assert
    with pytest.raises(InvalidFileFormat, match="Missing required columns"):
        LV_Parser(_zip_bytesio_file(mock_file))


def test_lv_parse_valid_data():
    # Arrange
    mock_file = io.BytesIO(
        b"""
        <products>
            <product>
                <product_id>A2</product_id>
                <original_name>Attack 2</original_name>
                <Extra>android</Extra>
            </product>
            <product>
                <product_id>2B</product_id>
                <original_name>2 Mo. Battle</original_name>
                <Extra>android</Extra>
            </product>
        </products>
        """
    )

    # Act
    parser = LV_Parser(_zip_bytesio_file(mock_file))
    parser.parse()

    # Assert
    assert sorted(parser._df.columns) == [
        "drug_code", "drug_name", "properties"]
    assert parser._df.iloc[0]["drug_code"] == "A2"
    assert parser._df.iloc[0]["drug_name"] == "Attack 2"
    assert parser._df.iloc[0]["properties"] == {"Extra": "android"}


def test_extract_xml_from_an_empty_zip():
    empty_zip = io.BytesIO()
    with zipfile.ZipFile(empty_zip, 'w') as zf:
        pass
    empty_zip.seek(0)

    with pytest.raises(FileNotFoundError, match="No XML file found in ZIP."):
        _extract_xml_from_zip(empty_zip)
