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

    # More robust concatenation approach with audio normalization
    ffmpeg_command = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',
        '-i', 'videoList.txt',
        '-filter_complex', 
        '[0:v]concat=n=' + str(len(video_list)) + ':v=1:a=1[outv][outa]',
        '-map', '[outv]', 
        '-map', '[outa]',
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-ar', '44100',
        '-y',
        output_path
    ]
    
    try:
        # First attempt with complex filter
        process = subprocess.run(ffmpeg_command, capture_output=True, text=True)
        
        # If the complex filter fails, fall back to simpler method
        if process.returncode != 0:
            print("Complex concatenation failed, trying simpler method...")
            fallback_command = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', 'videoList.txt',
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-ar', '44100',
                '-y',
                output_path
            ]
            subprocess.run(fallback_command)
            
        os.remove('videoList.txt')
        print(f"Created: {os.path.basename(output_path)}")
        return True
    except Exception as e:
        print(f"Error running ffmpeg: {e}")
        if os.path.exists('videoList.txt'):
            os.remove('videoList.txt')
        return False

def merge_word_videos(word, include_intro_outro=True):
    with open(path_str(JSON_FILE), "r") as file:
        data = json.load(file)
    
    if word not in data:
        print(f"Word '{word}' not found in database")
        return False
    
    wordData = data[word]
    content_videos = []
    
    if "clipData" not in wordData or not wordData["clipData"]:
        print(f"No clip data found for '{word}'")
        return False
    
    # Check for intro and outro videos
    intro_path = os.path.join(path_str(MERGED_VIDEOS_DIR), "intro.mp4")
    outro_path = os.path.join(path_str(MERGED_VIDEOS_DIR), "outro.mp4")
    
    has_intro = os.path.exists(intro_path) and include_intro_outro
    has_outro = os.path.exists(outro_path) and include_intro_outro
    
    if has_intro:
        print("Found intro video")
    else:
        print("Intro video not found or excluded")
    
    if has_outro:
        print("Found outro video")
    else:
        print("Outro video not found or excluded")
    
    print(f"Looking for merged video clips for: {word}")
    
    for index in wordData["clipData"].keys():
        video_path = os.path.join(path_str(MERGED_VIDEOS_DIR), f"{word}{index}.mp4")
        if os.path.exists(video_path):
            content_videos.append(video_path)
            print(f"Found clip {index}")

    if len(content_videos) >= 1:
        # Step 1: Merge content videos first
        content_only_path = os.path.join(path_str(FINAL_VIDEOS_DIR), f"{word}_content_temp.mp4")
        print(f"Merging {len(content_videos)} content videos for {word.upper()}")
        content_success = concat_videos(content_videos, content_only_path)
        
        if not content_success:
            print(f"Failed to merge content videos for {word}")
            return False
            
        final_output_path = os.path.join(path_str(FINAL_VIDEOS_DIR), f"{word.capitalize()}.mp4")
        
        # If no intro/outro needed, just rename the content file
        if not has_intro and not has_outro:
            try:
                os.rename(content_only_path, final_output_path)
                print(f"Final video created: {word.capitalize()}.mp4")
                print(f"Saved to: {path_str(FINAL_VIDEOS_DIR)}")
                return True
            except Exception as e:
                print(f"Error renaming file: {e}")
                return False
        
        # Step 2: Add intro and outro separately using file-based concatenation
        print("Adding intro and outro...")
        
        # Prepare list of files to concatenate in order
        final_list = []
        if has_intro:
            final_list.append(intro_path)
            print("Adding intro")
        
        final_list.append(content_only_path)
        
        if has_outro:
            final_list.append(outro_path)
            print("Adding outro")
        
        # Final merge with simple concatenation
        final_success = concat_videos(final_list, final_output_path)
        
        # Cleanup temporary file
        if os.path.exists(content_only_path):
            os.remove(content_only_path)
            
        if final_success:
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
    include_intro_outro = True
    
    if len(sys.argv) > 1:
        word = sys.argv[1].lower().strip()
        
        # Check for optional second parameter (0 = exclude intro/outro)
        if len(sys.argv) > 2 and sys.argv[2] == "0":
            include_intro_outro = False
            print("Excluding intro and outro videos")
        
        merge_word_videos(word, include_intro_outro)
    else:
        # word = input("Enter the word to create final video for: ").lower().strip()
        word = "abate"
        if word:
            merge_word_videos(word, include_intro_outro)
        else:
            print("No word provided. Exiting.")

