import logging
import sys
from config import config


def setup_logging():
    """
    Set up logging configuration based on config.yaml settings.
    """
    logging_config = config.get("logging", {})

    # Set default values if not specified
    level = logging_config.get("level", "INFO").upper()
    log_format = logging_config.get(
        "format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    date_format = logging_config.get("datefmt", "%Y-%m-%d %H:%M:%S")

    # Create a root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level, logging.INFO))

    # Define formatters
    formatter = logging.Formatter(fmt=log_format, datefmt=date_format)

    # Console Handler
    console_handler_config = logging_config.get("handlers", {}).get("console", {})
    console_level = console_handler_config.get("level", level).upper()
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, console_level, logging.INFO))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler
    file_handler_config = logging_config.get("handlers", {}).get("file", {})
    if file_handler_config:
        file_level = file_handler_config.get("level", level).upper()
        filename = file_handler_config.get("filename", "upload_playlist.log")
        mode = file_handler_config.get("mode", "a")
        encoding = file_handler_config.get("encoding", "utf-8")

        file_handler = logging.FileHandler(
            filename=filename, mode=mode, encoding=encoding
        )
        file_handler.setLevel(getattr(logging, file_level, logging.INFO))
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


# Initialize the logger
logger = setup_logging()
