# YouTube Playlist Uploader

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python script to upload multiple playlists from a CSV file to YouTube Music. It checks for existing playlists to avoid duplicates and adds songs accordingly.

## Table of Contents

- [YouTube Playlist Uploader](#youtube-playlist-uploader)
  - [Table of Contents](#table-of-contents)
  - [Prerequisites](#prerequisites)
  - [Setup](#setup)
    - [Running the Script](#running-the-script)
    - [Step-by-Step Guide](#step-by-step-guide)
  - [Usage](#usage)
  - [Project Structure](#project-structure)
  - [Troubleshooting](#troubleshooting)
  - [License](#license)

## Prerequisites

- Python 3.6 or higher
- `pipenv` installed
- Google account with YouTube access

## Setup

**Clone the Repository:**

```bash
git clone https://github.com/yourusername/youtube-playlist-uploader.git
cd youtube-playlist-uploader
```

After cloning the repository, you can set up the project using the following methods:

### Running the Script

Run the following commands to set up the project:

```bash
./setup.sh
```

### Step-by-Step Guide

1. **Install pipenv (If Not Already Installed):**

   ```bash
   pip install --user pipenv
   ```

2. **Install Dependencies:**

   ```bash
   pipenv install
   ```

   If you have development dependencies:

   ```bash
   pipenv install --dev
   ```

3. **Configure Google API Credentials:**

   Follow the YouTube Data API Setup Guide to obtain credentials.json.
   Place `credentials.json` inside the `credentials/` directory.

## Usage

1. Prepare Your CSV File:

   - Ensure your CSV file follows the structure:

     ```csv
     Track name,Artist name,Album,Playlist name,Type,ISRC,Spotify - id
     Song1,Artist1,Album1,Playlist1,Type1,ISRC1,SpotifyID1
     Song2,Artist2,Album2,Playlist2,Type2,ISRC2,SpotifyID2
     Place the CSV file inside the data/ directory. Rename it to playlist.csv or update the script accordingly.
     ```

   - Place the CSV file inside the data/ directory. Rename it to playlist.csv or update the script accordingly.

2. Run the Script:

   - Before running your project, activate the `pipenv` shell:

     ```bash
     pipenv shell
     ```

   - Running the Main Script

     ```bash
     python src/main.py
     ```

     > Alternative: You can run the script without activating the shell using pipenv run:

     ```bash
     pipenv run python src/main.py
     ```

   The script will:

   - Detect and handle CSV encoding.
   - Check for existing playlists.
   - Create new playlists if they don't exist.
   - Add songs to their respective playlists.

## Project Structure

```txt
your_project/
├── data/
│ ├── playlist.csv
│ └── playlist_prod.csv
├── src/
│ ├── **init**.py
│ ├── main.py
│ ├── detect_encoding.py
│ └── test_auth.py
├── credentials/
│ └── credentials.json
├── .gitignore
├── requirements.txt
├── README.md
└── myenv/ # Virtual environment directory
├── bin/
├── lib/
├── pyvenv.cfg
└── ...
```

## Troubleshooting

- Encoding Errors:

  - Ensure your CSV file is saved in a supported encoding (UTF-8, ISO-8859-1, etc.).
  - Use tools like **chardet** to detect and specify the correct encoding.

- Authentication Issues:

  - Verify that `credentials.json is` correctly placed inside the `credentials/` directory.
  - Delete `token.pickle` if re-authentication is required.

- API Quota Exceeded:

  - Monitor your API usage in the Google Cloud Console.
  - Implement rate limiting in the script to reduce the number of API calls.

- Dependency Conflicts:
- If you encounter dependency conflicts, try the following:

  - Clear caches using `pipenv --clear`
  - Remove the `Pipfile.lock` file. `rm Pipfile.lock`
  - Run `pipenv install` to regenerate the lock file.
  - Update the dependencies using `pipenv update`.
  - Check for specific versions in the `Pipfile` are compatible.

## License

[MIT](https://github.com/qqharry21/youtube-playlist-uploader/tree/main?tab=MIT-1-ov-file)
