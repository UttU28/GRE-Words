# GRE Words Video Generator

This project automates the creation of vocabulary learning videos for GRE preparation. The system extracts words from a PDF, collects video clips showing word usage from movies, and creates educational videos.

## Directory Structure

- `resources/` - Contains all resource files:
  - `fonts/` - Font files for text rendering
  - `woKyaBolRahi.png` - Main background image
  - `woKyaBolRahiEnd.png` - End image for videos
  - `bkpgreWords.json` - Word data
  - `endVideo.mp4` - Video to append at the end
  - `fillerVideo.mp4` - Optional filler video 
  - `wordList.pdf` - Source PDF with GRE words

- `images/` - Generated images for each word
- `downloadedVideos/` - Raw video clips downloaded from the web
- `mergedVideos/` - Videos with words and definitions
- `finalVideos/` - Final combined videos for each word

## Setup

1. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Ensure you have ffmpeg installed on your system
   - Windows: Download from https://ffmpeg.org/download.html
   - Linux: `sudo apt install ffmpeg`
   - Mac: `brew install ffmpeg`

3. Make sure all resource files are in the `resources/` directory
   - Required fonts should be in `resources/fonts/`
   - Background images should be in `resources/`

## Configuration

This project uses a centralized configuration system with `.env` file. All file paths and settings can be modified there.

The main settings are:
- Directory paths for various file types
- Font and image file names
- Chrome debugging port for web automation

## Process Workflow

1. `0_extractingWords.py` - Extracts words and meanings from the PDF file
2. `1_collectVideoData.py` - Collects video clips from movies showing word usage
3. `2_downloadingVideos.py` - Downloads the video clips
4. `3_makeImages.py` - Creates images with the word and its definition
5. `4_addVideoToImage.py` - Combines images with video clips
6. `5_mergeAllOneByOne.py` - Merges all clips for each word into a final video

## Running the Scripts

Run the scripts in numerical order. Some scripts support batch processing to handle portions of the word list at a time.

Example:
```bash
python 0_extractingWords.py
python 1_collectVideoData.py
# ... and so on
```

## Customization

To customize the look and feel:
- Replace image files in `resources/` 
- Modify font settings in `.env`
- Adjust video parameters in the script files as needed
