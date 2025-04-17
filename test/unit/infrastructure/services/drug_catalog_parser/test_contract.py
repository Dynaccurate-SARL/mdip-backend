import pytest
import pandas as pd
from io import BytesIO
from unittest.mock import AsyncMock

from src.infrastructure.services.drug_parser.contract import Parser
from src.infrastructure.services.drug_parser.exc import (
    InvalidParsedData, MissingPreExecutionError)


class DummyParser(Parser):
    def _open_and_validate(self) -> bool:
        self._df = pd.DataFrame({
            "drug_name": ["Aspirin", "Ibuprofen"],
            "drug_code": ["ASP123", "IBU456"],
            "properties": [{"type": "tablet"}, {"type": "capsule"}]
        })
        return True

    def parse(self):
        pass


@pytest.mark.asyncio
async def test_save_all():
    # Arrange
    file = BytesIO(b"dummy content")
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


class DummyParserInvalidParsedColumns(Parser):
    def _open_and_validate(self) -> bool:
        self._df = pd.DataFrame({
            "drug_name": ["Aspirin", "Ibuprofen"],
            "drug_code": [1, 2],
            "property": ["tablet", "capsule"]
        })
        return True

    def parse(self):
        pass


@pytest.mark.asyncio
async def test_save_all_with_invalid_parsed_columns():
    # Arrange
    file = BytesIO(b"dummy content")
    parser = DummyParserInvalidParsedColumns(file)

    # Act & Assert
    with pytest.raises(InvalidParsedData, match="Invalid dataframe columns"):
        await parser.save_all(AsyncMock(), 1)


class DummyParserInvalidColumnsTypes(Parser):
    def _open_and_validate(self) -> bool:
        self._df = pd.DataFrame({
            "drug_name": ["Aspirin", "Ibuprofen"],
            "drug_code": [1, 2],
            "properties": ["tablet", "capsule"]
        })
        return True

    def parse(self):
        pass


@pytest.mark.asyncio
async def test_save_all_with_invalid_data_types():
    # Arrange
    file = BytesIO(b"dummy content")
    parser = DummyParserInvalidColumnsTypes(file)

    # Act & Assert
    with pytest.raises(InvalidParsedData,
                       match="Invalid data types in dataframe"):
        await parser.save_all(AsyncMock(), 1)


class DummyParserNone(Parser):
    def _open_and_validate(self) -> bool:
        self._df = None

    def parse(self):
        pass


@pytest.mark.asyncio
async def test_save_all_with_missing_pre_execution():
    # Arrange
    file = BytesIO(b"dummy content")
    parser = DummyParserNone(file)

    mock_session = AsyncMock()
    mock_connection = AsyncMock()
    mock_session.connection.return_value = mock_connection
    mock_connection.run_sync = AsyncMock()

    catalog_id = 1

    # Act & Assert
    with pytest.raises(MissingPreExecutionError):
        await parser.save_all(mock_session, catalog_id)
