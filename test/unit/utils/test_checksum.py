import pytest
from io import BytesIO
from fastapi import UploadFile

from src.utils.checksum import filepath_checksum, dict_hash

@pytest.mark.asyncio
async def test_file_checksum_consistent_hashing():
    # Arrange
    file_content = b"Test content for checksum"
    file = UploadFile(filename="test.txt", file=BytesIO(file_content))

    # Act
    hash1 = await filepath_checksum(file)
    file.file.seek(0)  # Reset file pointer
    hash2 = await filepath_checksum(file)

    # Assert
    assert hash1 == hash2, \
        "Hashing the same file should produce consistent results"


@pytest.mark.asyncio
async def test_file_checksum_different_content_different_hash():
    # Arrange
    file1 = UploadFile(filename="test1.txt", file=BytesIO(b"Content A"))
    file2 = UploadFile(filename="test2.txt", file=BytesIO(b"Content B"))

    # Act
    hash1 = await filepath_checksum(file1)
    hash2 = await filepath_checksum(file2)

    # Assert
    assert hash1 != hash2, \
        "Hashing files with different content should produce different hashes"


@pytest.mark.asyncio
async def test_file_checksum_empty_file():
    # Arrange
    file = UploadFile(filename="empty.txt", file=BytesIO(b""))

    # Act
    hash_value = await filepath_checksum(file)

    # Assert
    assert isinstance(hash_value, str), \
        "Hash of an empty file should be a string"
    assert len(hash_value) > 0, "Hash of an empty file should not be empty"


@pytest.mark.asyncio
async def test_file_checksum_custom_algorithm():
    # Arrange
    file_content = b"Test content for checksum"
    file = UploadFile(filename="test.txt", file=BytesIO(file_content))

    # Act
    hash_sha256 = await filepath_checksum(file, algorithm="sha256")
    file.file.seek(0)  # Reset file pointer
    hash_md5 = await filepath_checksum(file, algorithm="md5")

    # Assert
    assert hash_sha256 != hash_md5, \
        "Hashes generated with different algorithms should not be the same"


@pytest.mark.parametrize(
    "data,algorithm,expected_length",
    [
        ({"key": "value"}, "sha256", 64),
        ({"key": "value"}, "md5", 32),
        ({"key": "value"}, "sha1", 40),
    ],
)
def test_dict_hash_algorithm_length(data, algorithm, expected_length):
    # Act
    hash_value = dict_hash(data, algorithm=algorithm)

    # Assert
    assert len(hash_value) == expected_length, \
        f"Hash length for {algorithm} should be {expected_length}"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "file_content,algorithm,expected_length",
    [
        (b"Test content", "sha256", 64),
        (b"Test content", "md5", 32),
        (b"Test content", "sha1", 40),
    ],
)
async def test_file_checksum_algorithm_length(file_content, algorithm, expected_length):
    # Arrange
    file = UploadFile(filename="test.txt", file=BytesIO(file_content))

    # Act
    hash_value = await filepath_checksum(file, algorithm=algorithm)

    # Assert
    assert len(hash_value) == expected_length, \
        f"Hash length for {algorithm} should be {expected_length}"
