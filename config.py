import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Function to get env var with fallback
def getEnvVar(varName, default=None, required=False):
    value = os.getenv(varName, default)
    if required and value is None:
        print(f"Error: Environment variable {varName} is required but not set")
        sys.exit(1)
    return value

# Base directory paths - resolve absolute paths
BASE_DIR = Path(getEnvVar('BASE_DIR', os.path.dirname(os.path.abspath(__file__)))).resolve()
RESOURCES_DIR = Path(getEnvVar('RESOURCES_DIR', os.path.join(BASE_DIR, 'resources'))).resolve()
FONTS_DIR = Path(getEnvVar('FONTS_DIR', os.path.join(RESOURCES_DIR, 'fonts'))).resolve()
DATA_DIR = Path(getEnvVar('DATA_DIR', os.path.join(RESOURCES_DIR, 'data'))).resolve()

# Data directory paths
JSON_FILE = Path(getEnvVar('JSON_FILE', os.path.join(RESOURCES_DIR, 'greWords.json'))).resolve()
SCR_CHROME_DATA_DIR = Path(getEnvVar('SCR_CHROME_DATA_DIR', os.path.join(RESOURCES_DIR, 'chromeData', 'scrapingChromeData'))).resolve()
INS_CHROME_DATA_DIR = Path(getEnvVar('INS_CHROME_DATA_DIR', os.path.join(RESOURCES_DIR, 'chromeData', 'instagramChromeData'))).resolve()

# Media directory paths
IMAGES_DIR = Path(getEnvVar('IMAGES_DIR', os.path.join(DATA_DIR, 'images'))).resolve()
DOWNLOADED_VIDEOS_DIR = Path(getEnvVar('DOWNLOADED_VIDEOS_DIR', os.path.join(DATA_DIR, 'downloadedVideos'))).resolve()
MERGED_VIDEOS_DIR = Path(getEnvVar('MERGED_VIDEOS_DIR', os.path.join(DATA_DIR, 'mergedVideos'))).resolve()
FINAL_VIDEOS_DIR = Path(getEnvVar('FINAL_VIDEOS_DIR', os.path.join(DATA_DIR, 'finalVideos'))).resolve()

# Resource files
BACKGROUND_IMAGE = Path(getEnvVar('BACKGROUND_IMAGE', os.path.join(RESOURCES_DIR, 'woKyaBolRahi.png'))).resolve()
END_IMAGE = Path(getEnvVar('END_IMAGE', os.path.join(RESOURCES_DIR, 'woKyaBolRahiEnd.png'))).resolve()
END_VIDEO = Path(getEnvVar('END_VIDEO', os.path.join(RESOURCES_DIR, 'endVideo.mp4'))).resolve()
FILLER_VIDEO = Path(getEnvVar('FILLER_VIDEO', os.path.join(RESOURCES_DIR, 'fillerVideo.mp4'))).resolve()

# Font files
WORD_FONT = getEnvVar('WORD_FONT', 'Word.ttf')
MEANING_FONT = getEnvVar('MEANING_FONT', 'Meaning.ttf')
MOVIE_FONT = getEnvVar('MOVIE_FONT', 'Movie.ttf')
DEFAULT_FONT = getEnvVar('DEFAULT_FONT', 'Roboto-Black.ttf')

# PDF File
PDF_FILE = Path(getEnvVar('PDF_FILE', os.path.join(RESOURCES_DIR, 'wordList.pdf'))).resolve()

# Chrome Configuration
DEBUGGING_PORT = getEnvVar('DEBUGGING_PORT', '9004')
CHROME_PATH = getEnvVar('CHROME_PATH', None)

# List of all directories that need to be created
ALL_DIRECTORIES = [
    RESOURCES_DIR,
    FONTS_DIR,
    DATA_DIR,
    IMAGES_DIR,
    DOWNLOADED_VIDEOS_DIR,
    MERGED_VIDEOS_DIR,
    FINAL_VIDEOS_DIR,
    os.path.join(RESOURCES_DIR, 'chromeData')
]

# Function to ensure directories exist
def ensureDirsExist(quiet=False):
    os.makedirs(DATA_DIR, exist_ok=True)
    
    for directory in ALL_DIRECTORIES:
        try:
            os.makedirs(directory, exist_ok=True)
        except Exception as e:
            print(f"Error creating directory {directory}: {e}")
    

def pathStr(path):
    return str(path)

# Auto-create directories when config is imported
ensureDirsExist(quiet=True) 