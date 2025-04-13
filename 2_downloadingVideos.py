import os
import json
import requests
import time
import concurrent.futures
from config import JSON_FILE, DOWNLOADED_VIDEOS_DIR, path_str, ensure_dirs_exist
from tqdm import tqdm
from colorama import init, Fore, Style
import sys

# Initialize colorama
init(autoreset=True)

# Color formatting functions
def success(text): return f"{Fore.GREEN}{text}{Style.RESET_ALL}"
def error(text): return f"{Fore.RED}{text}{Style.RESET_ALL}"
def info(text): return f"{Fore.CYAN}{text}{Style.RESET_ALL}"
def warning(text): return f"{Fore.YELLOW}{text}{Style.RESET_ALL}"
def highlight(text): return f"{Fore.MAGENTA}{Style.BRIGHT}{text}{Style.RESET_ALL}"

# Function to download a single clip
def download_clip(word, clip_index, video_url):
    file_path = os.path.join(path_str(DOWNLOADED_VIDEOS_DIR), f"{word}{clip_index}.mp4")
    
    # Skip if file already exists
    if os.path.exists(file_path):
        return {"status": "skipped", "word": word, "clip_index": clip_index, "size_mb": 0}
    
    try:
        # Start a GET request with streaming enabled
        response = requests.get(video_url, stream=True)
        response.raise_for_status()
        
        # Download the file
        with open(file_path, "wb") as video_file:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    video_file.write(chunk)
        
        # Get file size
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        
        return {
            "status": "success", 
            "word": word, 
            "clip_index": clip_index, 
            "size_mb": file_size_mb
        }
        
    except Exception as e:
        return {
            "status": "failed", 
            "word": word, 
            "clip_index": clip_index, 
            "error": str(e),
            "size_mb": 0
        }

def download_word_videos(target_word, max_workers=4):
    ensure_dirs_exist()
    
    with open(path_str(JSON_FILE), "r") as file:
        data = json.load(file)
    
    if target_word not in data:
        print(error(f"Word '{target_word}' not found in database"))
        return
    
    word_data = data[target_word]
    
    if "clipData" not in word_data or not word_data["clipData"]:
        print(warning(f"No clips found for '{target_word}'"))
        return
    
    total_clips = len(word_data["clipData"])
    
    print(highlight(f"\nDownloading videos for: {target_word.upper()}"))
    print(f"Found {total_clips} clips to download")
    
    download_tasks = []
    for clip_index, clip_info in word_data["clipData"].items():
        download_tasks.append((target_word, clip_index, clip_info["videoURL"]))
    
    try:
        user_input = 8
        # user_input = input(f"Enter number of parallel downloads (default: {max_workers}): ").strip()
        if user_input:
            max_workers = int(user_input)
            if max_workers < 1:
                max_workers = 1
            elif max_workers > 16:
                print(warning("Too many parallel downloads may cause issues. Limiting to 16."))
                max_workers = 16
    except ValueError:
        print(warning(f"Invalid input. Using default ({max_workers}) parallel downloads."))
    
    print(info(f"Starting downloads with {max_workers} parallel workers"))
    
    successful_downloads = 0
    failed_downloads = 0
    already_downloaded = 0
    total_size_mb = 0
    
    progress_bar = tqdm(total=total_clips, desc=f"Downloading {target_word}", unit="clip")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_task = {
            executor.submit(download_clip, target_word, clip_index, url): (target_word, clip_index) 
            for target_word, clip_index, url in download_tasks
        }
        
        for future in concurrent.futures.as_completed(future_to_task):
            result = future.result()
            progress_bar.update(1)
            
            if result["status"] == "success":
                successful_downloads += 1
                total_size_mb += result["size_mb"]
            elif result["status"] == "skipped":
                already_downloaded += 1
            else:
                failed_downloads += 1
    
    progress_bar.close()
    
    print(highlight("\nDOWNLOAD SUMMARY"))
    print(f"{info('Total clips:')} {total_clips}")
    print(f"{success('Successfully downloaded:')} {successful_downloads}")
    print(f"{warning('Already downloaded (skipped):')} {already_downloaded}")
    print(f"{error('Failed downloads:')} {failed_downloads}")
    print(f"{info('Total data downloaded:')} {total_size_mb:.2f} MB")
    
    if failed_downloads == 0 and successful_downloads > 0:
        print(success(f"\n✓ Download complete for {target_word}!"))
    elif failed_downloads > 0:
        print(warning(f"\n⚠ Download completed with {failed_downloads} failures."))
    else:
        print(error("\n✗ No new downloads completed."))
    
    return {
        "total": total_clips,
        "success": successful_downloads,
        "skipped": already_downloaded,
        "failed": failed_downloads,
        "size_mb": total_size_mb
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        word = sys.argv[1].lower().strip()
        download_word_videos(word)
    else:
        # word = input("Enter the word to download videos for: ").strip().lower()
        word = "abate"
        if word:
            download_word_videos(word)
        else:
            print(error("No word provided. Exiting."))
