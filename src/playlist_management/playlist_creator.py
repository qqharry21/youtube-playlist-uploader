from googleapiclient.errors import HttpError
from config import config
from logger import logger


def create_playlist(youtube, title, description=""):
    """Create a new YouTube playlist."""
    try:
        request = youtube.playlists().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": ["Python", "YouTube", "API"],
                    "defaultLanguage": "en",
                },
                "status": {
                    "privacyStatus": config.get(
                        "privacy_status", "private"
                    )  # Use config
                },
            },
        )
        response = request.execute()
        logger.info(
            f"Created playlist: {response['snippet']['title']} (ID: {response['id']})"
        )
        return response["id"]
    except HttpError as e:
        logger.error(f"An HTTP error occurred while creating playlist '{title}': {e}")
        return None


def get_existing_playlists(youtube):
    """Retrieve a dictionary of existing playlists with playlist names as keys and IDs as values."""
    playlists = {}
    try:
        request = youtube.playlists().list(
            part="snippet",
            mine=True,
            maxResults=50,  # Adjust as needed; YouTube API allows up to 50 per request
        )
        while request:
            response = request.execute()
            for item in response.get("items", []):
                name = item["snippet"]["title"]
                pid = item["id"]
                playlists[name.lower()] = (
                    pid  # Using lowercase for case-insensitive comparison
                )
            request = youtube.playlists().list_next(request, response)
        logger.debug(f"Retrieved {len(playlists)} existing playlists.")
    except HttpError as e:
        logger.error(f"An HTTP error occurred while retrieving existing playlists: {e}")
    return playlists
