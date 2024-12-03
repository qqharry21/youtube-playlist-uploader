import pytest
import pandas as pd
from unittest.mock import MagicMock, patch
from src.utils.encoding_detector import detect_file_encoding


@pytest.fixture(scope="session")
def test_csv_path():
    """
    Provides the path to the test CSV file.
    """
    return "data/playlist.csv"


@pytest.fixture(scope="session")
def load_test_csv(test_csv_path):
    """
    Loads the test CSV file into a pandas DataFrame.
    """
    try:
        encoding = detect_file_encoding(test_csv_path)
        df = pd.read_csv(test_csv_path, encoding=encoding)
        # Drop rows with missing critical data
        df.dropna(
            subset=["Track name", "Artist name", "Playlist name", "Spotify - id"],
            inplace=True,
        )
        # Ensure correct data types
        df["Playlist name"] = df["Playlist name"].astype(str)
        df["Spotify - id"] = df["Spotify - id"].astype(str)
        return df
    except FileNotFoundError:
        pytest.fail(f"Test CSV file '{test_csv_path}' not found.")
    except pd.errors.EmptyDataError:
        pytest.fail(f"Test CSV file '{test_csv_path}' is empty.")
    except Exception as e:
        pytest.fail(f"An error occurred while loading the test CSV: {e}")


@pytest.fixture(scope="session")
def mock_youtube_service():
    """
    Mocks the YouTube service with necessary methods.
    """
    youtube = MagicMock()

    # Mock playlists().insert().execute() for creating playlists
    youtube.playlists().insert.return_value.execute.side_effect = lambda: {
        "id": "PLNEW123"
    }

    # Mock playlistItems().insert().execute() for adding songs
    youtube.playlistItems().insert.return_value.execute.side_effect = lambda: {
        "id": "ITEM123"
    }

    # Mock playlists().list().execute() for retrieving existing playlists
    youtube.playlists().list.return_value.execute.side_effect = lambda: {
        "items": [{"id": "PLEXIST123", "snippet": {"title": "Existing Playlist"}}]
    }

    return youtube


@pytest.fixture(scope="session")
def mock_functions():
    """
    Mocks helper functions like search_video and get_existing_videos.
    """
    mock_search_video = MagicMock(
        side_effect=[
            "VID123",  # For "There's Nothing Holdin' Me Back"
            "VID456",  # For "Solo Dance"
            "VID789",  # For "Feelin' Myself"
            "VID101112",  # For "Feels (feat. Pharrell Williams, Katy Perry & Big Sean)"
            "VID131415",  # For "I’m So Sorry"
            "VID161718",  # For "All Night"
            "VID192021",  # For "根本不是我對手"
            "VID222324",  # For "Shape of You"
            "VID252627",  # For "Blinding Lights"
            "VID282930",  # For "Don't Start Now"
            "VID313233",  # For "Dance Monkey"
            "VID343536",  # For "Levitating (feat. DaBaby)"
            "VID373839",  # For "Bad Guy"
            "VID404142",  # For "Bohemian Rhapsody"
            "VID434445",  # For "Hotel California"
            "VID464748",  # For "Stairway to Heaven"
            "VID495051",  # For "Imagine"
            "VID525354",  # For "Hey Jude"
            "VID555657",  # For "Let It Be"
            "VID585960",  # For "Smells Like Teen Spirit"
            "VID616263",  # For "Losing My Religion"
            "VID646566",  # For "Creep"
            "VID676869",  # For "Duplicate Song"
            "VID707172",  # For "Duplicate Song"
            None,  # For "Missing Spotify ID" (No video found)
            "VID737475",  # For "Rock & Roll (Live)"
            "VID798081",  # For "La Bicicleta"
            "VID828384",  # For "This is an exceptionally long track name..."
        ]
    )

    mock_get_existing_videos = MagicMock(return_value=[])

    return mock_search_video, mock_get_existing_videos
