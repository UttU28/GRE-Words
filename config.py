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
DATA_DIR = Path(get_env_var('DATA_DIR', os.path.join(BASE_DIR, 'data'))).resolve()

# Data directory paths
JSON_FILE = Path(get_env_var('JSON_FILE', os.path.join(RESOURCES_DIR, 'greWords.json'))).resolve()
CHROME_DATA_DIR = Path(get_env_var('CHROME_DATA_DIR', os.path.join(BASE_DIR, 'chromeData'))).resolve()

# Media directory paths
IMAGES_DIR = Path(get_env_var('IMAGES_DIR', os.path.join(DATA_DIR, 'images'))).resolve()
DOWNLOADED_VIDEOS_DIR = Path(get_env_var('DOWNLOADED_VIDEOS_DIR', os.path.join(DATA_DIR, 'downloadedVideos'))).resolve()
MERGED_VIDEOS_DIR = Path(get_env_var('MERGED_VIDEOS_DIR', os.path.join(DATA_DIR, 'mergedVideos'))).resolve()
FINAL_VIDEOS_DIR = Path(get_env_var('FINAL_VIDEOS_DIR', os.path.join(DATA_DIR, 'finalVideos'))).resolve()

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
CHROME_PATH = get_env_var('CHROME_PATH', None)

# List of all directories that need to be created
ALL_DIRECTORIES = [
    RESOURCES_DIR,
    FONTS_DIR,
    DATA_DIR,
    IMAGES_DIR,
    DOWNLOADED_VIDEOS_DIR,
    MERGED_VIDEOS_DIR,
    FINAL_VIDEOS_DIR
]

# Function to ensure directories exist
def ensure_dirs_exist(quiet=False):
    """Create all necessary directories if they don't exist"""
    if not quiet:
        print("\nEnsuring directories exist...")
        print(f"BASE_DIR: {BASE_DIR}")
        print(f"DATA_DIR: {DATA_DIR}")
    
    # Make sure DATA_DIR is created first, as other dirs depend on it
    os.makedirs(DATA_DIR, exist_ok=True)
    
    for directory in ALL_DIRECTORIES:
        try:
            path_str_dir = str(directory)
            os.makedirs(directory, exist_ok=True)
            if not quiet:
                print(f"Ensured directory exists: {directory}")
                if os.path.exists(directory):
                    print(f"  - Confirmed {directory} exists")
                else:
                    print(f"  - WARNING: {directory} still doesn't exist after creation attempt")
        except Exception as e:
            print(f"Error creating directory {directory}: {e}")
    
    if not quiet:
        print("\nDirectory structure ready!")

# Convert pathlib Paths to strings where needed
def path_str(path):
    """Convert Path object to string for compatibility"""
    return str(path)

# Auto-create directories when config is imported
ensure_dirs_exist(quiet=True) 