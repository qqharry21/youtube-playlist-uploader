import os
import sys
import pandas as pd
import time
from authentication.youtube_auth import authenticate_youtube
from playlist_management.playlist_creator import (
    create_playlist,
    get_existing_playlists,
)
from playlist_management.playlist_adder import (
    add_video_to_playlist,
    get_existing_videos,
    search_video,
)
from utils.encoding_detector import detect_file_encoding
from config import config
from logger import logger

# Constants
TRACK_COL_NAME = "Track name"
ARTIST_COL_NAME = "Artist name"
PLAYLIST_COL_NAME = "Playlist name"


def parse_playlist_csv(file_path):
    """Parse the playlist CSV file and return a dictionary grouping songs by Playlist name."""
    try:
        encoding = detect_file_encoding(file_path)
        if encoding is None:
            logger.warning("Could not detect encoding. Using 'utf-8' as fallback.")
            encoding = "utf-8"
        df = pd.read_csv(
            file_path, encoding=encoding, on_bad_lines="skip"
        )  # For pandas >=1.3.0
        # Check if required columns exist
        required_columns = [TRACK_COL_NAME, ARTIST_COL_NAME, PLAYLIST_COL_NAME]
        if not all(column in df.columns for column in required_columns):
            missing = [col for col in required_columns if col not in df.columns]
            logger.error(
                f"CSV file is missing the following required columns: {missing}"
            )
            sys.exit(1)
        # Drop rows with missing Playlist name, Track name, or Artist name
        df = df.dropna(subset=[PLAYLIST_COL_NAME, TRACK_COL_NAME, ARTIST_COL_NAME])
        # Normalize text by stripping whitespace and converting to title case
        df[PLAYLIST_COL_NAME] = (
            df[PLAYLIST_COL_NAME].astype(str).str.strip().str.title()
        )
        df[TRACK_COL_NAME] = df[TRACK_COL_NAME].astype(str).str.strip()
        df[ARTIST_COL_NAME] = df[ARTIST_COL_NAME].astype(str).str.strip().str.title()
        # Group by Playlist name
        grouped = df.groupby(PLAYLIST_COL_NAME)
        playlists = {}
        for playlist_name, group in grouped:
            # Combine Track name and Artist name to form search queries
            group["Search Query"] = (
                group[TRACK_COL_NAME].astype(str)
                + " "
                + group[ARTIST_COL_NAME].astype(str)
            )
            songs = group["Search Query"].tolist()
            playlists[playlist_name] = songs
        logger.debug(f"Parsed CSV and found {len(playlists)} unique playlists.")
        return playlists
    except FileNotFoundError:
        logger.error(f"Playlist file '{file_path}' not found.")
        sys.exit(1)
    except pd.errors.EmptyDataError:
        logger.error(f"Playlist file '{file_path}' is empty.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error reading playlist file: {e}")
        sys.exit(1)


def process_playlists(youtube, playlist_name, songs, existing_playlists):
    logger.info(f"\nProcessing Playlist: '{playlist_name}'")
    playlist_id = get_or_create_playlist(youtube, playlist_name, existing_playlists)
    if not playlist_id:
        return

    existing_videos = get_existing_videos(youtube, playlist_id)
    logger.info(
        f"   * Retrieved {len(existing_videos)} existing songs in the playlist."
    )
    add_songs_to_playlist(youtube, songs, playlist_id, existing_videos)


def get_or_create_playlist(youtube, playlist_name, existing_playlists):
    playlist_id = existing_playlists.get(playlist_name.lower())
    if playlist_id:
        logger.info(
            f" - Playlist exists with ID: {playlist_id}. Adding songs to existing playlist."
        )
    else:
        logger.info(" - Playlist does not exist. Creating new playlist.")
        playlist_description = (
            f"Uploaded via Python script from CSV. Playlist: {playlist_name}"
        )
        playlist_id = create_playlist(youtube, playlist_name, playlist_description)
        if not playlist_id:
            logger.error(f"   * Failed to create playlist '{playlist_name}'. Skipping.")
            return None
        logger.info(f"   * Created playlist '{playlist_name}' with ID: {playlist_id}")
        existing_playlists[playlist_name.lower()] = playlist_id
    return playlist_id


def add_songs_to_playlist(youtube, songs, playlist_id, existing_videos):
    logger.info(f"   * Adding {len(songs)} songs to playlist:")
    for idx, song in enumerate(songs, start=1):
        logger.info(f"     {idx}. Searching for: {song}")
        video_id = search_video(youtube, song)
        if video_id:
            if video_id in existing_videos:
                logger.info(
                    f"        - Video ID {video_id} already exists in the playlist. Skipping."
                )
            else:
                add_video_to_playlist(youtube, video_id, playlist_id)
                existing_videos.append(video_id)
                logger.info(f"        - Added Video ID {video_id} to playlist.")
                time.sleep(1)
        else:
            logger.warning(f"        - No video found for '{song}'. Skipping.")


def main():
    logger.info("Starting YouTube Playlist Uploader.")

    youtube = authenticate_youtube()
    existing_playlists = get_existing_playlists(youtube)
    logger.info(f"Retrieved {len(existing_playlists)} existing playlists from YouTube.")

    playlist_file = config.get("playlist_file", os.path.join("data", "playlist.csv"))
    playlists = parse_playlist_csv(playlist_file)
    logger.info(f"Found {len(playlists)} unique playlists in the CSV.")

    for playlist_name, songs in playlists.items():
        process_playlists(youtube, playlist_name, songs, existing_playlists)

    print("\nAll playlists have been processed and uploaded.")


if __name__ == "__main__":
    main()
