import os
import json
import re
import subprocess
from config import (
    JSON_FILE, IMAGES_DIR, DOWNLOADED_VIDEOS_DIR, MERGED_VIDEOS_DIR,
    path_str, ensure_dirs_exist
)

# Ensure necessary directories exist
ensure_dirs_exist()

def mergingVideoAndImage(imageLocation, videoLocation, outputLocation, videoStartHeight):
    # Use fixed height for consistent video display
    fixed_height = 500  # Set fixed height for all videos

    ffmpeg_command = [
        'ffmpeg',
        '-loop', '1', '-i', imageLocation,
        '-i', videoLocation,
        '-filter_complex', f'[1]scale=-1:{fixed_height}[scaled];[scaled]setpts=PTS-STARTPTS[inner];[0][inner]overlay=(W-w)/2:{videoStartHeight+60}:shortest=1[out]',
        '-map', '[out]', '-map', '1:a',
        '-c:a', 'copy',
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        '-pix_fmt', 'yuv420p',
        '-y', outputLocation
    ]
    try:
        subprocess.run(ffmpeg_command)
        print(f"Successfully merged {os.path.basename(imageLocation)} with {os.path.basename(videoLocation)}")
    except Exception as e:
        print(f"Error running ffmpeg: {e}")

# Load JSON data
with open(path_str(JSON_FILE), "r") as allWords:
    allWordsData = json.load(allWords)

def addVideoToImage(start_index, end_index):
    for currentWord, wordData in list(allWordsData.items())[start_index:end_index]:
        currentDef = wordData['meaning']
        print(f"Processing word: {currentWord}")
        
        # Check if clipData exists
        if "clipData" not in wordData or not wordData["clipData"]:
            print(f"No clip data found for {currentWord}, skipping")
            continue
            
        # Process all clips for this word
        for index, videoData in wordData["clipData"].items():
            imageLocation = os.path.join(path_str(IMAGES_DIR), f"{currentWord}{index}.png")
            videoLocation = os.path.join(path_str(DOWNLOADED_VIDEOS_DIR), f"{currentWord}{index}.mp4")
            outputLocation = os.path.join(path_str(MERGED_VIDEOS_DIR), f"{currentWord}{index}.mp4")
            
            # Check if files exist
            if not os.path.exists(imageLocation):
                print(f"Image not found: {imageLocation}")
                continue
                
            if not os.path.exists(videoLocation):
                print(f"Video not found: {videoLocation}")
                continue
            
            # Get videoStartHeight from data or use a default value
            videoStartHeight = videoData.get("videoStartHeight", 300)
            
            print(f"Merging video and image for {currentWord}, index = {index}")
            mergingVideoAndImage(imageLocation, videoLocation, outputLocation, videoStartHeight)
            print(f"Done with {currentWord}, index = {index}")
        
        print(f"Completed all clips for word: {currentWord}")

# Determine batch size and process
batch_size = 10
num_batches = (len(allWordsData) + batch_size - 1) // batch_size

print(f"Found {len(allWordsData)} words in JSON file")
print(f"Processing in batches of {batch_size} words ({num_batches} batches total)")

try:
    batch_input = input("Enter batch number to process (default 1): ").strip()
    batch_number = int(batch_input) if batch_input else 1
    
    if 1 <= batch_number <= num_batches:
        start_index = (batch_number - 1) * batch_size
        end_index = min(batch_number * batch_size, len(allWordsData))
        print(f"Processing batch {batch_number} (words {start_index+1} to {end_index})")
        addVideoToImage(start_index, end_index)
    else:
        print(f"Invalid batch number. Please enter a number between 1 and {num_batches}.")
except ValueError:
    print("Invalid input. Please enter a number.")
except KeyboardInterrupt:
    print("\nProcess interrupted by user")
except Exception as e:
    print(f"Unexpected error: {e}")