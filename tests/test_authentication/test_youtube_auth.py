import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Adjust the path to import src modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from src.authentication.youtube_auth import authenticate_youtube


@pytest.fixture
def mock_build():
    with patch("src.authentication.youtube_auth.build") as mock_build_func:
        yield mock_build_func


@pytest.fixture
def mock_installed_app_flow():
    with patch("src.authentication.youtube_auth.InstalledAppFlow") as mock_flow:
        mock_flow.from_client_secrets_file.return_value.run_local_server.return_value = (
            MagicMock()
        )
        yield mock_flow


def test_authenticate_youtube_existing_token(mock_build, mock_installed_app_flow):
    """
    Test authenticate_youtube when token.pickle exists and is valid.
    """
    with patch("src.authentication.youtube_auth.os.path.exists") as mock_exists, patch(
        "src.authentication.youtube_auth.pickle"
    ) as mock_pickle, patch("src.authentication.youtube_auth.Request") as mock_request:

        mock_exists.return_value = True
        mock_pickle.load.return_value = MagicMock(valid=True, refresh_token=True)

        youtube_service = MagicMock()
        mock_build.return_value = youtube_service

        service = authenticate_youtube()

        assert service == youtube_service
        mock_build.assert_called_once_with(
            "youtube", "v3", credentials=mock_pickle.load.return_value
        )


def test_authenticate_youtube_invalid_token(mock_build, mock_installed_app_flow):
    """
    Test authenticate_youtube when token.pickle exists but is invalid or expired.
    """
    with patch("src.authentication.youtube_auth.os.path.exists") as mock_exists, patch(
        "src.authentication.youtube_auth.pickle"
    ) as mock_pickle, patch("src.authentication.youtube_auth.Request") as mock_request:

        mock_exists.return_value = True
        mock_creds = MagicMock(valid=False, expired=True, refresh_token=True)
        mock_pickle.load.return_value = mock_creds

        youtube_service = MagicMock()
        mock_build.return_value = youtube_service

        service = authenticate_youtube()

        assert service == youtube_service
        mock_creds.refresh.assert_called_once()
        mock_build.assert_called_once_with("youtube", "v3", credentials=mock_creds)


def test_authenticate_youtube_no_token(mock_build, mock_installed_app_flow):
    """
    Test authenticate_youtube when token.pickle does not exist.
    """
    with patch("src.authentication.youtube_auth.os.path.exists") as mock_exists, patch(
        "src.authentication.youtube_auth.pickle"
    ) as mock_pickle, patch(
        "src.authentication.youtube_auth.InstalledAppFlow.from_client_secrets_file"
    ) as mock_flow_instance, patch(
        "src.authentication.youtube_auth.sys"
    ) as mock_sys:

        mock_exists.return_value = False
        mock_flow_instance.return_value.run_local_server.return_value = MagicMock()
        youtube_service = MagicMock()
        mock_build.return_value = youtube_service

        with patch("src.authentication.youtube_auth.open", mock_open=MagicMock()):
            service = authenticate_youtube()

        assert service == youtube_service
        mock_flow_instance.assert_called_once_with(
            "credentials/credentials.json", ["https://www.googleapis.com/auth/youtube"]
        )
        mock_build.assert_called_once_with(
            "youtube",
            "v3",
            credentials=mock_flow_instance.return_value.run_local_server.return_value,
        )
        mock_pickle.dump.assert_called_once()


def mock_open(mock=None, data=None):
    if mock is None:
        mock = MagicMock()
    handle = MagicMock()
    handle.read.return_value = data
    mock.return_value = handle
    return mock
