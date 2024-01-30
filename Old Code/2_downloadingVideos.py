import os
import json
import requests

file_path = "greWords.json"

with open(file_path, "r") as file:
    data = json.load(file)

outputDirectory = "downloadedVideos"
os.makedirs(outputDirectory, exist_ok=True)

# Iterate through each word in the data
for currentWord, wordData in data.items():
    # Iterate through each clipData for the word
    for clip_index, clip_info in wordData["clipData"].items():
        video_url = clip_info["videoURL"]
        video_info = clip_info["videoInfo"]

        os.makedirs(outputDirectory+"\\"+currentWord, exist_ok=True)

        # Generate a file name based on word, clip index, and video info
        file_name = f"{currentWord}_clip{clip_index}_{video_info.replace(' ', '_')}.mp4"
        file_path = os.path.join(outputDirectory, currentWord +"\\"+ clip_index + ".mp4")

        # Download the video
        response = requests.get(video_url, stream=True)
        with open(file_path, "wb") as video_file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    video_file.write(chunk)

        print(f"Downloaded video: {file_name}")
