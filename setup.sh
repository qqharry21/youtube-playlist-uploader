#!/bin/bash

# =====================================================================
# setup.sh - Automate the setup of the YouTube Playlist Uploader Project
# =====================================================================

# Exit immediately if a command exits with a non-zero status
set -e

# Function to print informational messages in blue
echo_info() {
    echo -e "\033[1;34m[INFO]\033[0m $1"
}

# Function to print error messages in red
echo_error() {
    echo -e "\033[1;31m[ERROR]\033[0m $1"
}

# Function to print success messages in green
echo_success() {
    echo -e "\033[1;32m[SUCCESS]\033[0m $1"
}

# =====================================================================
# 1. Check for Python Installation
# =====================================================================
echo_info "Checking for Python installation..."

if ! command -v python3 &> /dev/null
then
    echo_error "Python3 could not be found. Please install Python 3.8 or higher."
    exit 1
else
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    REQUIRED_VERSION="3.8"
    if [[ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]]; then
        echo_error "Python version $PYTHON_VERSION detected. Python $REQUIRED_VERSION or higher is required."
        exit 1
    fi
    echo_success "Python $PYTHON_VERSION is installed."
fi

# =====================================================================
# 2. Check and Install pipenv
# =====================================================================
echo_info "Checking for pipenv installation..."

if ! command -v pipenv &> /dev/null
then
    echo_info "pipenv not found. Installing pipenv..."
    pip3 install --user pipenv
    # Add ~/.local/bin to PATH if not already
    if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
        echo_info "Adding ~/.local/bin to PATH."
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
        # For Zsh users, uncomment the following line
        # echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
        source ~/.bashrc
    fi
    echo_success "pipenv installed successfully."
else
    echo_success "pipenv is already installed."
fi

# =====================================================================
# 3. Initialize pipenv Environment
# =====================================================================
echo_info "Initializing pipenv environment..."

# Define default Python version
DEFAULT_PYTHON_VERSION="3.8"

# Read Python version from config.yaml if it exists
if [ -f "config.yaml" ]; then
    PYTHON_VERSION=$(grep -E "^python_version:" config.yaml | awk '{print $2}')
    if [ -z "$PYTHON_VERSION" ]; then
        PYTHON_VERSION="$DEFAULT_PYTHON_VERSION"
        echo_info "Python version not specified in config.yaml. Using default Python $PYTHON_VERSION."
    else
        echo_info "Using Python version $PYTHON_VERSION from config.yaml."
    fi
else
    PYTHON_VERSION="$DEFAULT_PYTHON_VERSION"
    echo_info "config.yaml not found. Using default Python $PYTHON_VERSION."
fi

# Initialize pipenv with the specified Python version if Pipfile doesn't exist
if [ ! -f "Pipfile" ]; then
    echo_info "Pipfile not found. Initializing pipenv with Python $PYTHON_VERSION."
    pipenv --python $PYTHON_VERSION
else
    echo_info "Pipfile already exists. Skipping pipenv initialization."
fi

# =====================================================================
# 4. Install Project Dependencies
# =====================================================================
echo_info "Installing project dependencies with pipenv..."

pipenv install

# =====================================================================
# Additional Step: Install Development Dependencies (if separate)
# =====================================================================

# This step is optional if you included dev-packages in the previous pipenv install
echo_info "Installing development dependencies with pipenv..."

pipenv install --dev

echo_success "Development dependencies installed successfully."

echo_success "Project dependencies installed successfully."

# =====================================================================
# 5. Ensure __init__.py Files Exist
# =====================================================================
echo_info "Ensuring __init__.py files exist in src/ and its subdirectories..."

declare -a dirs=("src" "src/authentication" "src/playlist_management" "src/utils")

for dir in "${dirs[@]}"
do
    if [ ! -f "$dir/__init__.py" ]; then
        touch "$dir/__init__.py"
        echo_info "Created __init__.py in $dir."
    else
        echo_info "__init__.py already exists in $dir."
    fi
done

echo_success "All necessary __init__.py files are in place."

# =====================================================================
# 6. Create Default config.yaml if Not Exists
# =====================================================================
if [ ! -f "config.yaml" ]; then
    echo_info "Creating default config.yaml..."
    cat <<EOL > config.yaml
# Configuration File for YouTube Playlist Uploader

credentials_path: "credentials/credentials.json"
playlist_file: "data/playlist.csv"
log_file: "upload_playlist.log"
privacy_status: "private"  # Options: 'public', 'private', 'unlisted'
video_category_id: "10"    # Category ID for Music
python_version: "3.8"      # Specify Python version if needed

logging:
  level: "INFO"                  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  datefmt: "%Y-%m-%d %H:%M:%S"
  handlers:
    console:
      level: "INFO"
    file:
      level: "INFO"
      filename: "upload_playlist.log"
      mode: "a"  # Append mode
      encoding: "utf-8"
      max_bytes: 10485760  # 10 MB
      backup_count: 5
EOL
    echo_success "config.yaml created with default configurations."
else
    echo_info "config.yaml already exists. Skipping creation."
fi

# =====================================================================
# 7. Create Credentials Directory
# =====================================================================
if [ ! -d "credentials" ]; then
    echo_info "Creating credentials directory..."
    mkdir credentials
    echo_success "credentials/ directory created."
else
    echo_info "credentials/ directory already exists. Skipping creation."
fi

# =====================================================================
# 8. Prompt User to Place credentials.json
# =====================================================================
if [ ! -f "credentials/credentials.json" ]; then
    echo_error "Missing 'credentials/credentials.json' file."
    echo_info "Please place your Google API credentials in the 'credentials/' directory."
else
    echo_success "credentials.json found."
fi

# =====================================================================
# 9. Create or Update .gitignore
# =====================================================================
echo_info "Setting up .gitignore..."

if [ ! -f ".gitignore" ]; then
    echo_info ".gitignore not found. Creating .gitignore..."
    cat <<EOL > .gitignore
# Virtual environment
myenv/
.venv/
Pipfile.lock

# Sensitive credentials
credentials/credentials.json
token.pickle

# Python cache
__pycache__/
*.pyc

# Logs
*.log

# OS-specific files
.DS_Store
Thumbs.db
EOL
    echo_success ".gitignore created."
else
    echo_info ".gitignore already exists. Ensuring necessary entries are present."

    # Append missing entries if necessary
    declare -a gitignore_entries=(
        "# Virtual environment"
        "myenv/"
        ".venv/"
        "Pipfile.lock"
        ""
        "# Sensitive credentials"
        "credentials/credentials.json"
        "token.pickle"
        ""
        "# Python cache"
        "__pycache__/"
        "*.pyc"
        ""
        "# Logs"
        "*.log"
        ""
        "# OS-specific files"
        ".DS_Store"
        "Thumbs.db"
    )

    for entry in "${gitignore_entries[@]}"
    do
        grep -qxF "$entry" .gitignore || echo "$entry" >> .gitignore
    done

    echo_success ".gitignore updated."
fi

# =====================================================================
# 10. Final Instructions
# =====================================================================
echo_success "Setup completed successfully!"

echo_info "Next Steps:"
echo_info "1. Place your 'credentials.json' file in the 'credentials/' directory."
echo_info "2. Activate the pipenv virtual environment:"
echo_info "   \`pipenv shell\`"
echo_info "3. Run your main script:"
echo_info "   \`python src/main.py\`"
echo_info "   Or, without activating the shell:"
echo_info "   \`pipenv run python src/main.py\`"
