import os
import json
import sys
import subprocess
from config import (
    JSON_FILE, MERGED_VIDEOS_DIR, FINAL_VIDEOS_DIR,
    path_str, ensure_dirs_exist
)

# Ensure necessary directories exist
ensure_dirs_exist()

def concat_videos(video_list, output_path):
    if not video_list:
        return False
        
    with open('videoList.txt', 'w') as file:
        for video in video_list:
            file.write(f"file '{video}'\n")

    ffmpeg_command = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',
        '-i', 'videoList.txt',
        '-c', 'copy',
        '-y',
        output_path
    ]
    
    try:
        subprocess.run(ffmpeg_command)
        os.remove('videoList.txt')
        print(f"Created: {os.path.basename(output_path)}")
        return True
    except Exception as e:
        print(f"Error running ffmpeg: {e}")
        if os.path.exists('videoList.txt'):
            os.remove('videoList.txt')
        return False

def merge_word_videos(word):
    with open(path_str(JSON_FILE), "r") as file:
        data = json.load(file)
    
    if word not in data:
        print(f"Word '{word}' not found in database")
        return False
    
    wordData = data[word]
    videos_to_merge = []
    
    if "clipData" not in wordData or not wordData["clipData"]:
        print(f"No clip data found for '{word}'")
        return False
    
    print(f"Looking for merged video clips for: {word}")
    
    for index in wordData["clipData"].keys():
        video_path = os.path.join(path_str(MERGED_VIDEOS_DIR), f"{word}{index}.mp4")
        if os.path.exists(video_path):
            videos_to_merge.append(video_path)
            print(f"Found clip {index}")

    if len(videos_to_merge) >= 1:
        print(f"Merging {len(videos_to_merge)} videos for {word.upper()}")
        output_path = os.path.join(path_str(FINAL_VIDEOS_DIR), f"{word.capitalize()}.mp4")
        success = concat_videos(videos_to_merge, output_path)
        
        if success:
            print(f"Final video created: {word.capitalize()}.mp4")
            print(f"Saved to: {path_str(FINAL_VIDEOS_DIR)}")
            return True
        else:
            print(f"Failed to create final video for {word}")
            return False
    else:
        print(f"No merged videos found for {word}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        word = sys.argv[1].lower().strip()
        merge_word_videos(word)
    else:
        word = input("Enter the word to create final video for: ").lower().strip()
        if word:
            merge_word_videos(word)
        else:
            print("No word provided. Exiting.")

