import pytest
from unittest.mock import MagicMock, patch

# Adjust the path to import src modules
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.main import process_playlists


def test_process_playlists_create_new_playlist(mock_logger):
    """
    Test processing playlists when a new playlist needs to be created.
    """
    youtube = MagicMock()
    playlists = {"Test Playlist": ["Song 1 Artist A", "Song 2 Artist B"]}
    existing_playlists = {}

    # Mock create_playlist to return a new playlist ID
    from src.playlist_management.playlist_creator import create_playlist

    with patch(
        "src.main.create_playlist", return_value="PLNEW123"
    ) as mock_create_playlist, patch(
        "src.main.get_existing_videos", return_value=[]
    ), patch(
        "src.main.add_video_to_playlist"
    ) as mock_add_video:

        process_playlists(youtube, playlists, existing_playlists, mock_logger)

        # Verify that create_playlist was called
        mock_create_playlist.assert_called_once_with(
            youtube,
            "New Playlist",
            "Uploaded via Python script from CSV. Playlist: New Playlist",
        )

        # Verify that add_video_to_playlist was called twice
        assert mock_add_video.call_count == 2

        # Verify that existing_playlists was updated
        assert existing_playlists == {"new playlist": "PLNEW123"}


def test_process_playlists_existing_playlist(mock_logger):
    """
    Test processing playlists when the playlist already exists.
    """
    youtube = MagicMock()
    playlists = {"Existing Playlist": ["Song 1 Artist A", "Song 2 Artist B"]}
    existing_playlists = {"existing playlist": "PLEXIST123"}

    # Mock get_existing_videos to return existing video IDs
    from src.playlist_management.playlist_adder import get_existing_videos

    with patch(
        "src.main.get_existing_videos", return_value=["VID123", "VID456"]
    ), patch("src.main.search_video", side_effect=["VID789", "VID456"]), patch(
        "src.main.add_video_to_playlist"
    ) as mock_add_video:

        process_playlists(youtube, playlists, existing_playlists, mock_logger)

        # Verify that add_video_to_playlist was called once (for 'VID789')
        mock_add_video.assert_called_once_with(youtube, "VID789", "PLEXIST123")


def test_process_playlists_no_video_found(mock_logger):
    """
    Test processing playlists when no video is found for a song.
    """
    youtube = MagicMock()
    playlists = {"Test Playlist": ["Nonexistent Song Artist X"]}
    existing_playlists = {}

    with patch("src.main.create_playlist", return_value="PLTEST123"), patch(
        "src.main.get_existing_videos", return_value=[]
    ), patch("src.main.search_video", return_value=None), patch(
        "src.main.add_video_to_playlist"
    ) as mock_add_video:

        process_playlists(youtube, playlists, existing_playlists, mock_logger)

        # Verify that add_video_to_playlist was never called
        mock_add_video.assert_not_called()


@pytest.fixture
def mock_logger():
    with patch("src.main.logger") as mock_logger:
        yield mock_logger
