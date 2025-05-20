import pytest
import pandas as pd
from io import BytesIO

from src.infrastructure.services.pandas_parser.drug.exc import InvalidFileFormat
from src.infrastructure.services.pandas_parser.mapping.parse import DrugMapping, MappingParser


def make_csv_bytes(data: pd.DataFrame) -> bytes:
    buf = BytesIO()
    data.to_csv(buf, index=False)
    return buf.getvalue()


def test_mapping_parser_parses_valid_csv():
    # Arrange
    df = pd.DataFrame({
        "drug_code": ["A", "B"],
        "related_drug_code": ["X", "Y"]
    })
    csv_bytes = make_csv_bytes(df)

    # Act
    parser = MappingParser(csv_bytes)
    result = list(parser.parse(chunk_size=1))

    # Assert
    assert len(result) == 2
    assert isinstance(result[0][0], DrugMapping)
    assert result[0][0].drug_code == "A"
    assert result[1][0].related_drug_code == "Y"


def test_mapping_parser_raises_on_missing_columns():
    # Arrange
    df = pd.DataFrame({
        "drug_code": ["A"],
        "other_column": ["Z"]
    })
    csv_bytes = make_csv_bytes(df)

    # Act & Assert
    with pytest.raises(InvalidFileFormat):
        MappingParser(csv_bytes)


def test_mapping_parser_raises_on_invalid_csv():
    # Arrange
    invalid_bytes = b"not,a,csv"

    # Act & Assert
    with pytest.raises(InvalidFileFormat):
        MappingParser(invalid_bytes)


def test_mapping_parser_chunked_parsing():
    # Arrange
    df = pd.DataFrame({
        "drug_code": ["A", "B", "C"],
        "related_drug_code": ["X", "Y", "Z"]
    })
    csv_bytes = make_csv_bytes(df)

    # Act
    parser = MappingParser(csv_bytes)
    chunks = list(parser.parse(chunk_size=2))

    # Assert
    assert len(chunks) == 2
    assert len(chunks[0]) == 2
    assert len(chunks[1]) == 1
    assert chunks[0][0].drug_code == "A"
    assert chunks[1][0].drug_code == "C"
