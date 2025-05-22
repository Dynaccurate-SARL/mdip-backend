from io import BytesIO
import pytest
import pandas as pd
from unittest.mock import AsyncMock

from src.infrastructure.services.pandas_parser.drug.contract import PandasParser
from src.infrastructure.services.pandas_parser.drug.exc import (
    InvalidFileFormat, InvalidParsedData, MissingPreExecutionError)


class DummyInvalidFileParser(PandasParser):
    def _open(self):
        return pd.read_excel(self._file)

    def _required_columns(self):
        return []

    def parse(self):
        pass


def test_invalid_file():
    # Arrange
    file = BytesIO(b"dummy content")
    # Act & Assert
    with pytest.raises(InvalidFileFormat, match="Invalid file format"):
        DummyInvalidFileParser(file)

# ----------------------------------------------------------------------


class DummyParser(PandasParser):
    def _open(self):
        return pd.DataFrame({
            "drug_name": ["Aspirin", "Ibuprofen"],
            "drug_code": ["ASP123", "IBU456"],
            "properties": [{"type": "tablet"}, {"type": "capsule"}]
        })

    def _required_columns(self):
        return []

    def parse(self):
        pass


@pytest.mark.asyncio
async def test_save_all():
    # Arrange
    file = b"dummy content"
    parser = DummyParser(file)

    mock_session = AsyncMock()
    mock_connection = AsyncMock()
    mock_session.connection.return_value = mock_connection
    mock_connection.run_sync = AsyncMock()

    catalog_id = 1

    # Act
    await parser.save_all(mock_session, catalog_id)

    # Assert
    assert mock_connection.run_sync.called
    mock_connection.run_sync.assert_called_once()
    mock_session.commit.assert_called_once()

# ----------------------------------------------------------------------


class DummyParserInvalidParsedColumns(PandasParser):
    def _open(self):
        return pd.DataFrame({
            "drug_name": ["Aspirin", "Ibuprofen"],
            "drug_code": [1, 2],
            "property": ["tablet", "capsule"]
        })

    def _required_columns(self):
        return []

    def parse(self):
        pass


@pytest.mark.asyncio
async def test_save_all_with_invalid_parsed_columns():
    # Arrange
    file = b"dummy content"
    parser = DummyParserInvalidParsedColumns(file)

    # Act & Assert
    with pytest.raises(InvalidParsedData, match="Invalid dataframe columns"):
        await parser.save_all(AsyncMock(), 1)

# ----------------------------------------------------------------------


class DummyParserInvalidColumnsTypes(PandasParser):
    def _open(self):
        return pd.DataFrame({
            "drug_name": ["Aspirin", "Ibuprofen"],
            "drug_code": [1, 2],
            "properties": ["tablet", "capsule"]
        })

    def _required_columns(self):
        return []

    def parse(self):
        pass


@pytest.mark.asyncio
async def test_save_all_with_invalid_data_types():
    # Arrange
    file = b"dummy content"
    parser = DummyParserInvalidColumnsTypes(file)

    # Act & Assert
    with pytest.raises(InvalidParsedData,
                       match="Invalid data types in dataframe"):
        await parser.save_all(AsyncMock(), 1)

# ----------------------------------------------------------------------


class DummyParserNone(PandasParser):
    def _open(self):
        return None

    def _required_columns(self):
        return []

    def parse(self):
        pass


@pytest.mark.asyncio
async def test_save_all_with_missing_pre_execution():
    # Arrange
    file = b"dummy content"
    parser = DummyParserNone(file)

    mock_session = AsyncMock()
    mock_connection = AsyncMock()
    mock_session.connection.return_value = mock_connection
    mock_connection.run_sync = AsyncMock()

    catalog_id = 1

    # Act & Assert
    with pytest.raises(MissingPreExecutionError):
        await parser.save_all(mock_session, catalog_id)
