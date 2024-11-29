import chardet
from config import config
from logger import logger  # Import the logger


def detect_file_encoding(file_path=None, num_bytes=10000):
    """Detect the encoding of a file using chardet.

    Args:
        file_path (str, optional): Path to the file. Defaults to the playlist file from config.
        num_bytes (int, optional): Number of bytes to read for detection. Defaults to 10000.

    Returns:
        str: Detected encoding.
    """
    if file_path is None:
        file_path = config.get("playlist_file", "data/playlist.csv")
    try:
        with open(file_path, "rb") as f:
            raw_data = f.read(num_bytes)
        result = chardet.detect(raw_data)
        encoding = result["encoding"]
        confidence = result["confidence"]
        logger.info(f"Detected encoding: {encoding} with confidence {confidence}")
        return encoding
    except Exception as e:
        logger.error(f"Error detecting file encoding for '{file_path}': {e}")
        return None
