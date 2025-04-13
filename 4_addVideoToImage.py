import os
import json
import sys
import subprocess
from config import (
    JSON_FILE, IMAGES_DIR, DOWNLOADED_VIDEOS_DIR, MERGED_VIDEOS_DIR,
    path_str, ensure_dirs_exist
)

# Ensure necessary directories exist
ensure_dirs_exist()

def merge_video_and_image(imageLocation, videoLocation, outputLocation, videoStartHeight):
    fixed_height = 500
    
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
        print(f"Successfully merged: {os.path.basename(outputLocation)}")
        return True
    except Exception as e:
        print(f"Error running ffmpeg: {e}")
        return False

def process_word(word):
    with open(path_str(JSON_FILE), "r") as file:
        data = json.load(file)
    
    if word not in data:
        print(f"Word '{word}' not found in database")
        return False
        
    wordData = data[word]
    
    if "clipData" not in wordData or not wordData["clipData"]:
        print(f"No clip data found for '{word}'")
        return False
    
    clips_processed = 0
    clips_failed = 0
    
    print(f"Processing word: {word}")
    print(f"Found {len(wordData['clipData'])} clips to process")
    
    for index, videoData in wordData["clipData"].items():
        imageLocation = os.path.join(path_str(IMAGES_DIR), f"{word}{index}.png")
        videoLocation = os.path.join(path_str(DOWNLOADED_VIDEOS_DIR), f"{word}{index}.mp4")
        outputLocation = os.path.join(path_str(MERGED_VIDEOS_DIR), f"{word}{index}.mp4")
        
        # Check if files exist
        if not os.path.exists(imageLocation):
            print(f"Image not found: {imageLocation}")
            clips_failed += 1
            continue
            
        if not os.path.exists(videoLocation):
            print(f"Video not found: {videoLocation}")
            clips_failed += 1
            continue
        
        # Get videoStartHeight from data or use a default value
        videoStartHeight = videoData.get("videoStartHeight", 300)
        
        success = merge_video_and_image(imageLocation, videoLocation, outputLocation, videoStartHeight)
        if success:
            clips_processed += 1
        else:
            clips_failed += 1
    
    print(f"\nProcessing complete for '{word}'")
    print(f"Clips processed successfully: {clips_processed}")
    
    if clips_failed > 0:
        print(f"Clips failed: {clips_failed}")
    
    return clips_processed > 0

if __name__ == "__main__":
    if len(sys.argv) > 1:
        word = sys.argv[1].lower().strip()
        process_word(word)
    else:
        word = input("Enter the word to process videos for: ").lower().strip()
        if word:
            process_word(word)
        else:
            print("No word provided. Exiting.")