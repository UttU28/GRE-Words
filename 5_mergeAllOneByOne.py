import os
import json
import subprocess
from config import (
    JSON_FILE, MERGED_VIDEOS_DIR, FINAL_VIDEOS_DIR,
    path_str, ensure_dirs_exist
)

# Ensure necessary directories exist
ensure_dirs_exist()

def concatVideos(videoList, outputPath):
    with open('videoList.txt', 'w') as file:
        for video in videoList:
            file.write(f"file '{video}'\n")

    ffmpeg_command = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',  # Allow unsafe file names
        '-i', 'videoList.txt',
        '-c', 'copy',
        '-y',  # Overwrite output files without asking
        outputPath
    ]
    subprocess.run(ffmpeg_command)
    os.remove('videoList.txt')
    print(f"Created: {os.path.basename(outputPath)}")

# Load JSON data
with open(path_str(JSON_FILE), "r") as allWords:
    allWordsData = json.load(allWords)

print(f"Processing {len(allWordsData)} words...")
words_processed = 0

for currentWord, wordData in allWordsData.items():
    videosToMerge = []
    
    # Check if clipData exists
    if "clipData" in wordData:
        # Get all clips from clipData
        for index in wordData["clipData"].keys():
            video_path = os.path.join(path_str(MERGED_VIDEOS_DIR), f"{currentWord}{index}.mp4")
            if os.path.exists(video_path):
                videosToMerge.append(video_path)
                print(f"Found clip {index} for {currentWord}")

    if len(videosToMerge) >= 1:
        print(f"Merging {len(videosToMerge)} videos for {currentWord.upper()}")
        outputPath = os.path.join(path_str(FINAL_VIDEOS_DIR), f"{currentWord.capitalize()}.mp4")
        concatVideos(videosToMerge, outputPath)
        words_processed += 1
    else:
        print(f"No videos found for {currentWord}, skipping")

print(f"Completed! Processed {words_processed} words with videos.")
print(f"Final videos saved to: {path_str(FINAL_VIDEOS_DIR)}")

