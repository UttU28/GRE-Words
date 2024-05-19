import os
import json
import requests

file_path = "videoResources/greWords.json"

with open(file_path, "r") as file:
    data = json.load(file)

outputDirectory = "downloadedVideos/"
os.makedirs(outputDirectory, exist_ok=True)

# Function to download videos for a specific batch
def download_batch(start_index, end_index):
    for currentWord, wordData in list(data.items())[start_index:end_index]:
        for clip_index, clip_info in wordData["clipData"].items():
            video_url = clip_info["videoURL"]
            video_info = clip_info["videoInfo"]

            file_name = f"{currentWord}_clip{clip_index}_{video_info.replace(' ', '_')}.mp4"
            file_path = os.path.join(outputDirectory, file_name)

            response = requests.get(video_url, stream=True)
            with open(file_path, "wb") as video_file:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        video_file.write(chunk)

            print(f"Downloaded video: {file_name}")

# Define batch size
batch_size = 10

# Calculate the number of batches
num_batches = (len(data) + batch_size - 1) // batch_size

try:
    batch_number = 1
    if 1 <= batch_number <= num_batches:
        start_index = (batch_number - 1) * batch_size
        end_index = min(batch_number * batch_size, len(data))
        download_batch(start_index, end_index)
    else:
        print("Invalid batch number.")
except ValueError:
    print("Invalid input. Please enter a number.")
