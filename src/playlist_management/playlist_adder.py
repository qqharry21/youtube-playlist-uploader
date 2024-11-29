from googleapiclient.errors import HttpError
from config import config
from logger import logger


def add_video_to_playlist(youtube, video_id, playlist_id):
    """Add a video to the specified playlist."""
    try:
        request = youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {"kind": "youtube#video", "videoId": video_id},
                }
            },
        )
        response = request.execute()
        logger.info(f"Added video ID {video_id} to playlist ID {playlist_id}.")
    except HttpError as e:
        logger.error(f"An HTTP error occurred while adding video ID {video_id}: {e}")


def get_existing_videos(youtube, playlist_id):
    """Retrieve a list of video IDs already in the playlist."""
    video_ids = []
    try:
        request = youtube.playlistItems().list(
            part="snippet", playlistId=playlist_id, maxResults=50  # Max per request
        )
        while request:
            response = request.execute()
            for item in response.get("items", []):
                video_ids.append(item["snippet"]["resourceId"]["videoId"])
            request = youtube.playlistItems().list_next(request, response)
        logger.debug(
            f"Retrieved {len(video_ids)} existing videos in playlist ID {playlist_id}."
        )
    except HttpError as e:
        logger.error(f"An HTTP error occurred while retrieving existing videos: {e}")
    return video_ids


def search_video(youtube, query):
    """Search for a video on YouTube and return the first result's video ID."""
    try:
        request = youtube.search().list(
            part="snippet",
            maxResults=1,
            q=query,
            type="video",
            videoCategoryId=config.get("video_category_id", "10"),  # Use config
        )
        response = request.execute()
        items = response.get("items", [])
        if not items:
            logger.warning(f"No results found for '{query}'.")
            return None
        video_id = items[0]["id"]["videoId"]
        logger.debug(f"Found video ID {video_id} for query '{query}'.")
        return video_id
    except HttpError as e:
        logger.error(f"An HTTP error occurred while searching for '{query}': {e}")
        return None
