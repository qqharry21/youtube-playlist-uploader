import pytest
from unittest.mock import MagicMock, patch

# Adjust the path to import src modules
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.playlist_management.playlist_creator import (
    create_playlist,
    get_existing_playlists,
)


@pytest.fixture
def mock_youtube():
    youtube = MagicMock()
    yield youtube


def test_create_playlist_success(mock_youtube):
    """
    Test creating a playlist successfully.
    """
    mock_response = {"snippet": {"title": "Test Playlist"}, "id": "PL1234567890abcdef"}
    mock_youtube.playlists().insert().execute.return_value = mock_response

    playlist_id = create_playlist(mock_youtube, "Test Playlist", "A test playlist")

    assert playlist_id == "PL1234567890abcdef"
    mock_youtube.playlists().insert.assert_called_once_with(
        part="snippet,status",
        body={
            "snippet": {
                "title": "Test Playlist",
                "description": "A test playlist",
                "tags": ["Python", "YouTube", "API"],
                "defaultLanguage": "en",
            },
            "status": {"privacyStatus": "private"},
        },
    )


def test_create_playlist_http_error(mock_youtube):
    """
    Test creating a playlist when an HTTP error occurs.
    """
    from googleapiclient.errors import HttpError

    mock_youtube.playlists().insert().execute.side_effect = HttpError(
        MagicMock(status=403), "Forbidden"
    )

    with patch("src.playlist_management.playlist_creator.logger") as mock_logger:
        playlist_id = create_playlist(mock_youtube, "Test Playlist", "A test playlist")
        assert playlist_id is None
        mock_logger.error.assert_called_once()


def test_get_existing_playlists_success(mock_youtube):
    """
    Test retrieving existing playlists successfully.
    """
    mock_response_page1 = {
        "items": [
            {"snippet": {"title": "Playlist One"}, "id": "PL111"},
            {"snippet": {"title": "Playlist Two"}, "id": "PL222"},
        ],
        "nextPageToken": "TOKEN123",
    }
    mock_response_page2 = {
        "items": [
            {"snippet": {"title": "Playlist Three"}, "id": "PL333"},
        ],
        "nextPageToken": None,
    }

    mock_youtube.playlists().list.side_effect = [
        MagicMock(execute=MagicMock(return_value=mock_response_page1)),
        MagicMock(execute=MagicMock(return_value=mock_response_page2)),
    ]

    playlists = get_existing_playlists(mock_youtube)

    expected = {
        "playlist one": "PL111",
        "playlist two": "PL222",
        "playlist three": "PL333",
    }
    assert playlists == expected
    assert mock_youtube.playlists().list.call_count == 2


def test_get_existing_playlists_http_error(mock_youtube):
    """
    Test retrieving existing playlists when an HTTP error occurs.
    """
    from googleapiclient.errors import HttpError

    mock_youtube.playlists().list().execute.side_effect = HttpError(
        MagicMock(status=500), "Server Error"
    )

    with patch("src.playlist_management.playlist_creator.logger") as mock_logger:
        playlists = get_existing_playlists(mock_youtube)
        assert playlists == {}
        mock_logger.error.assert_called_once()
