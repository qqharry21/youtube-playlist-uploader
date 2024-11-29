import os
import pickle
import sys
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from config import config
from logger import logger

# Define the scopes
SCOPES = ["https://www.googleapis.com/auth/youtube"]


def authenticate_youtube():
    """Authenticate the user and return the YouTube service object."""
    creds = None
    token_path = "token.pickle"
    credentials_path = config["credentials_path"]

    # Token file stores the user's access and refresh tokens
    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            creds = pickle.load(token)
            logger.debug(f"Loaded credentials from {token_path}.")

    # If no valid credentials, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            logger.info("Refreshed expired credentials.")
        else:
            if not os.path.exists(credentials_path):
                logger.error(f"Missing '{credentials_path}' file.")
                sys.exit(1)
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
            logger.info("Obtained new credentials via OAuth flow.")

        # Save the credentials for future use
        with open(token_path, "wb") as token:
            pickle.dump(creds, token)
            logger.debug(f"Saved credentials to {token_path}.")

    try:
        youtube = build("youtube", "v3", credentials=creds)
        logger.info("Successfully built YouTube service object.")
        return youtube
    except Exception as e:
        logger.error(f"Error creating YouTube service: {e}")
        sys.exit(1)
