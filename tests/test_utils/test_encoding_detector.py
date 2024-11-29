import pytest
from unittest.mock import patch, mock_open
import sys
import os

# Adjust the path to import src modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.utils.encoding_detector import detect_file_encoding


def test_detect_file_encoding_success():
    """
    Test encoding detection with known encoding.
    """
    sample_bytes = b"This is a test file."
    with patch(
        "builtins.open", mock_open(read_data=sample_bytes)
    ) as mocked_file, patch(
        "src.utils.encoding_detector.config", {"playlist_file": "data/playlist.csv"}
    ):

        with patch(
            "src.utils.encoding_detector.chardet.detect",
            return_value={"encoding": "utf-8", "confidence": 1.0},
        ):
            encoding = detect_file_encoding()
            assert encoding == "utf-8"
            mocked_file.assert_called_once_with("data/playlist.csv", "rb")


def test_detect_file_encoding_none():
    """
    Test encoding detection when chardet returns None.
    """
    sample_bytes = b""
    with patch(
        "builtins.open", mock_open(read_data=sample_bytes)
    ) as mocked_file, patch(
        "src.utils.encoding_detector.config", {"playlist_file": "data/playlist.csv"}
    ):

        with patch(
            "src.utils.encoding_detector.chardet.detect",
            return_value={"encoding": None, "confidence": 0.0},
        ):
            encoding = detect_file_encoding()
            assert encoding is None
            mocked_file.assert_called_once_with("data/playlist.csv", "rb")


def test_detect_file_encoding_file_not_found():
    """
    Test encoding detection when the file does not exist.
    """
    with patch("src.utils.encoding_detector.os.path.exists", return_value=False), patch(
        "src.utils.encoding_detector.config",
        {"playlist_file": "data/missing_playlist.csv"},
    ), patch("src.utils.encoding_detector.logger") as mock_logger, patch(
        "builtins.open", side_effect=FileNotFoundError
    ):

        encoding = detect_file_encoding()
        assert encoding is None
        mock_logger.error.assert_called_once()


def test_detect_file_encoding_with_parameter():
    """
    Test encoding detection with a specified file path.
    """
    sample_bytes = b"Some other test data."
    with patch(
        "builtins.open", mock_open(read_data=sample_bytes)
    ) as mocked_file, patch(
        "src.utils.encoding_detector.chardet.detect",
        return_value={"encoding": "ISO-8859-1", "confidence": 0.95},
    ):

        encoding = detect_file_encoding(file_path="custom/path.csv")
        assert encoding == "ISO-8859-1"
        mocked_file.assert_called_once_with("custom/path.csv", "rb")
