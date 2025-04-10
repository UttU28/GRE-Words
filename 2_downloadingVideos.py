import os
import json
import requests
from config import JSON_FILE, DOWNLOADED_VIDEOS_DIR, path_str, ensure_dirs_exist

# Ensure necessary directories exist
ensure_dirs_exist()

# Load word data
with open(path_str(JSON_FILE), "r") as file:
    data = json.load(file)

# Iterate through each word in the data
for currentWord, wordData in data.items():
    print(f"Processing word: {currentWord}")
    # Iterate through each clipData for the word
    for clip_index, clip_info in wordData["clipData"].items():
        video_url = clip_info["videoURL"]
        video_info = clip_info["videoInfo"]

        # Format the filename to match what 4_addVideoToImage.py expects: wordNameclipIndex.mp4
        file_path = os.path.join(path_str(DOWNLOADED_VIDEOS_DIR), f"{currentWord}{clip_index}.mp4")

        print(f"Downloading video for {currentWord} (clip {clip_index}) from {video_url}")
        
        try:
            # Download the video
            response = requests.get(video_url, stream=True)
            response.raise_for_status()  # Check for download errors
            
            with open(file_path, "wb") as video_file:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        video_file.write(chunk)
                        
            print(f"Downloaded: {os.path.basename(file_path)}")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading {currentWord} clip {clip_index}: {e}")
        except Exception as e:
            print(f"Unexpected error for {currentWord} clip {clip_index}: {e}")

print("Video download process completed.")
