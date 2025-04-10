import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Function to get env var with fallback
def get_env_var(var_name, default=None, required=False):
    value = os.getenv(var_name, default)
    if required and value is None:
        print(f"Error: Environment variable {var_name} is required but not set")
        sys.exit(1)
    return value

# Base directory paths - resolve absolute paths
BASE_DIR = Path(get_env_var('BASE_DIR', os.path.dirname(os.path.abspath(__file__)))).resolve()
RESOURCES_DIR = Path(get_env_var('RESOURCES_DIR', os.path.join(BASE_DIR, 'resources'))).resolve()
FONTS_DIR = Path(get_env_var('FONTS_DIR', os.path.join(RESOURCES_DIR, 'fonts'))).resolve()

# Data directory paths
JSON_FILE = Path(get_env_var('JSON_FILE', os.path.join(RESOURCES_DIR, 'bkpgreWords.json'))).resolve()
CHROME_DATA_DIR = Path(get_env_var('CHROME_DATA_DIR', os.path.join(BASE_DIR, 'chromeData'))).resolve()

# Media directory paths
IMAGES_DIR = Path(get_env_var('IMAGES_DIR', os.path.join(BASE_DIR, 'images'))).resolve()
DOWNLOADED_VIDEOS_DIR = Path(get_env_var('DOWNLOADED_VIDEOS_DIR', os.path.join(BASE_DIR, 'downloadedVideos'))).resolve()
MERGED_VIDEOS_DIR = Path(get_env_var('MERGED_VIDEOS_DIR', os.path.join(BASE_DIR, 'mergedVideos'))).resolve()
FINAL_VIDEOS_DIR = Path(get_env_var('FINAL_VIDEOS_DIR', os.path.join(BASE_DIR, 'finalVideos'))).resolve()

# Resource files
BACKGROUND_IMAGE = Path(get_env_var('BACKGROUND_IMAGE', os.path.join(RESOURCES_DIR, 'woKyaBolRahi.png'))).resolve()
END_IMAGE = Path(get_env_var('END_IMAGE', os.path.join(RESOURCES_DIR, 'woKyaBolRahiEnd.png'))).resolve()
END_VIDEO = Path(get_env_var('END_VIDEO', os.path.join(RESOURCES_DIR, 'endVideo.mp4'))).resolve()
FILLER_VIDEO = Path(get_env_var('FILLER_VIDEO', os.path.join(RESOURCES_DIR, 'fillerVideo.mp4'))).resolve()

# Font files
WORD_FONT = get_env_var('WORD_FONT', 'Word.ttf')
MEANING_FONT = get_env_var('MEANING_FONT', 'Meaning.ttf')
MOVIE_FONT = get_env_var('MOVIE_FONT', 'Movie.ttf')
DEFAULT_FONT = get_env_var('DEFAULT_FONT', 'Roboto-Black.ttf')

# PDF File
PDF_FILE = Path(get_env_var('PDF_FILE', os.path.join(RESOURCES_DIR, 'wordList.pdf'))).resolve()

# Chrome Configuration
DEBUGGING_PORT = get_env_var('DEBUGGING_PORT', '9004')

# Ensure directories exist
def ensure_dirs_exist():
    """Create all necessary directories if they don't exist"""
    for directory in [RESOURCES_DIR, FONTS_DIR, IMAGES_DIR, 
                      DOWNLOADED_VIDEOS_DIR, MERGED_VIDEOS_DIR, FINAL_VIDEOS_DIR]:
        os.makedirs(directory, exist_ok=True)
        print(f"Ensured directory exists: {directory}")

# Convert pathlib Paths to strings where needed
def path_str(path):
    """Convert Path object to string for compatibility"""
    return str(path) 