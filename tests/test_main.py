# tests/test_main.py

import pytest
from unittest.mock import MagicMock, patch
import os
import sys

# Adjust the path to import src modules if necessary
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from main import (
    process_playlists,
)  # Adjust the import path based on your project structure


def test_process_playlists_create_new_playlist(
    load_test_csv, mock_youtube_service, mock_functions, mock_logger
):
    """
    Test processing playlists when new playlists need to be created.
    """
    # Extract fixtures
    df = load_test_csv
    youtube = mock_youtube_service
    mock_search_video, mock_get_existing_videos = mock_functions

    # Organize playlists from DataFrame
    playlists = {}
    for _, row in df.iterrows():
        playlist_name = row["Playlist name"]
        song = f"{row['Track name']} {row['Artist name']}"
        playlists.setdefault(playlist_name, []).append(song)

    # Initialize existing_playlists as empty to trigger creation
    existing_playlists = {}

    # Mock create_playlist, get_existing_videos, search_video, and add_video_to_playlist
    with patch(
        "main.create_playlist", return_value="PLNEW123"
    ) as mock_create_playlist, patch(
        "main.get_existing_videos", return_value=[]
    ), patch(
        "main.search_video", new=mock_search_video
    ), patch(
        "main.add_video_to_playlist"
    ) as mock_add_video:

        # Iterate over each playlist and process
        for playlist_name, songs in playlists.items():
            process_playlists(youtube, playlist_name, songs, existing_playlists)

        # Verify that create_playlist was called for each new playlist
        assert mock_create_playlist.call_count == len(
            playlists
        ), "create_playlist should be called for each new playlist."

        for playlist_name in playlists:
            mock_create_playlist.assert_any_call(
                youtube,
                playlist_name,
                f"Uploaded via Python script from CSV. Playlist: {playlist_name}",
            )

        # Verify that add_video_to_playlist was called for each song
        total_songs = sum(len(songs) for songs in playlists.values())
        assert (
            mock_add_video.call_count == total_songs
        ), f"add_video_to_playlist should be called {total_songs} times."

        # Verify that existing_playlists was updated correctly
        for playlist_name in playlists:
            assert (
                existing_playlists[playlist_name.lower()] == "PLNEW123"
            ), f"Playlist '{playlist_name}' should have ID 'PLNEW123'."


def test_process_playlists_existing_playlist(
    load_test_csv, mock_youtube_service, mock_functions, mock_logger
):
    """
    Test processing playlists when the playlist already exists.
    """
    # Extract fixtures
    df = load_test_csv
    youtube = mock_youtube_service
    mock_search_video, mock_get_existing_videos = mock_functions

    # Organize playlists from DataFrame
    playlists = {}
    for _, row in df.iterrows():
        playlist_name = row["Playlist name"]
        song = f"{row['Track name']} {row['Artist name']}"
        playlists.setdefault(playlist_name, []).append(song)

    # Initialize existing_playlists with one existing playlist
    existing_playlists = {"existing playlist": "PLEXIST123"}

    # Mock get_existing_videos to return existing video IDs
    with patch("main.get_existing_videos", return_value=["VID123", "VID456"]), patch(
        "main.search_video", side_effect=["VID789", "VID456", "VID101112", "VID131415"]
    ), patch("main.add_video_to_playlist") as mock_add_video, patch(
        "main.create_playlist", return_value="PLNEW456"
    ) as mock_create_playlist:

        # Iterate over each playlist and process
        for playlist_name, songs in playlists.items():
            process_playlists(youtube, playlist_name, songs, existing_playlists)

        # Identify new playlists that need to be created
        new_playlists = set(playlists.keys()) - {"Existing Playlist"}
        assert mock_create_playlist.call_count == len(
            new_playlists
        ), "create_playlist should be called only for new playlists."

        for playlist_name in new_playlists:
            mock_create_playlist.assert_any_call(
                youtube,
                playlist_name,
                f"Uploaded via Python script from CSV. Playlist: {playlist_name}",
            )

        # Calculate expected calls to add_video_to_playlist
        # Assuming "VID456" is a duplicate and should not be added again
        expected_calls = (
            sum(len(songs) for songs in playlists.values()) - 1
        )  # Subtract duplicates
        assert (
            mock_add_video.call_count == expected_calls
        ), f"add_video_to_playlist should be called {expected_calls} times."


def test_process_playlists_no_video_found(
    load_test_csv, mock_youtube_service, mock_functions, mock_logger
):
    """
    Test processing playlists when no video is found for a song.
    """
    # Extract fixtures
    youtube = mock_youtube_service
    mock_search_video, mock_get_existing_videos = mock_functions

    # Define a playlist with a song that will return None (no video found)
    playlists = {"Test Playlist": ["Nonexistent Song Artist X"]}

    # Initialize existing_playlists as empty to trigger creation
    existing_playlists = {}

    # Mock create_playlist, get_existing_videos, search_video, and add_video_to_playlist
    with patch(
        "main.create_playlist", return_value="PLTEST123"
    ) as mock_create_playlist, patch(
        "main.get_existing_videos", return_value=[]
    ), patch(
        "main.search_video", return_value=None
    ), patch(
        "main.add_video_to_playlist"
    ) as mock_add_video:

        # Iterate over each playlist and process
        for playlist_name, songs in playlists.items():
            process_playlists(youtube, playlist_name, songs, existing_playlists)

        # Verify that create_playlist was called once
        mock_create_playlist.assert_called_once_with(
            youtube,
            "Test Playlist",
            "Uploaded via Python script from CSV. Playlist: Test Playlist",
        )

        # Verify that add_video_to_playlist was never called since no video was found
        mock_add_video.assert_not_called()

        # Verify that existing_playlists was updated correctly
        assert (
            existing_playlists["test playlist"] == "PLTEST123"
        ), "Playlist 'Test Playlist' should have ID 'PLTEST123'."


@pytest.fixture
def mock_logger():
    with patch("main.logger") as mock_logger:
        yield mock_logger
