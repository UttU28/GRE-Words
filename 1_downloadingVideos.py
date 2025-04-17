import os
import requests
import time
import concurrent.futures
from config import DOWNLOADED_VIDEOS_DIR, pathStr, ensureDirsExist
from db_controller import db
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
def downloadClip(word, clipIndex, videoUrl):
    filePath = os.path.join(pathStr(DOWNLOADED_VIDEOS_DIR), f"{word}{clipIndex}.mp4")
    
    # Skip if file already exists
    if os.path.exists(filePath):
        return {"status": "skipped", "word": word, "clipIndex": clipIndex, "sizeMb": 0}
    
    try:
        # Start a GET request with streaming enabled
        response = requests.get(videoUrl, stream=True)
        response.raise_for_status()
        
        # Download the file
        with open(filePath, "wb") as videoFile:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    videoFile.write(chunk)
        
        # Get file size
        fileSizeMb = os.path.getsize(filePath) / (1024 * 1024)
        
        return {
            "status": "success", 
            "word": word, 
            "clipIndex": clipIndex, 
            "sizeMb": fileSizeMb
        }
        
    except Exception as e:
        return {
            "status": "failed", 
            "word": word, 
            "clipIndex": clipIndex, 
            "error": str(e),
            "sizeMb": 0
        }

def downloadWordVideos(targetWord, maxWorkers=4):
    ensureDirsExist()
    
    # Get word data from database
    wordData = db.getWord(targetWord)
    
    if not wordData:
        print(error(f"Word '{targetWord}' not found in database"))
        return
    
    wordId = wordData['id']
    clips = db.getClipsForWord(wordId)
    
    if not clips:
        print(warning(f"No clips found for '{targetWord}'"))
        return
    
    totalClips = len(clips)
    
    downloadTasks = []
    for clip in clips:
        downloadTasks.append((targetWord, clip['clip_index'], clip['video_url']))
    
    try:
        userInput = 8
        # userInput = input(f"Enter number of parallel downloads (default: {maxWorkers}): ").strip()
        if userInput:
            maxWorkers = int(userInput)
            if maxWorkers < 1:
                maxWorkers = 1
            elif maxWorkers > 16:
                print(warning("Too many parallel downloads may cause issues. Limiting to 16."))
                maxWorkers = 16
    except ValueError:
        print(warning(f"Invalid input. Using default ({maxWorkers}) parallel downloads."))
    
    successfulDownloads = 0
    failedDownloads = 0
    alreadyDownloaded = 0
    totalSizeMb = 0
    
    progressBar = tqdm(total=totalClips, desc=f"Downloading videos for: {targetWord.upper()}", unit="clip")
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=maxWorkers) as executor:
        futureToTask = {
            executor.submit(downloadClip, targetWord, clipIndex, url): (targetWord, clipIndex) 
            for targetWord, clipIndex, url in downloadTasks
        }
        
        for future in concurrent.futures.as_completed(futureToTask):
            result = future.result()
            progressBar.update(1)
            
            if result["status"] == "success":
                successfulDownloads += 1
                totalSizeMb += result["sizeMb"]
            elif result["status"] == "skipped":
                alreadyDownloaded += 1
            else:
                failedDownloads += 1
    
    progressBar.close()
    
    print(f"{info('Total data downloaded:')} {totalSizeMb:.2f} MB")
    
    if failedDownloads == 0 and successfulDownloads > 0:
        print(success(f"\nDownload complete for {targetWord}!"))
    elif failedDownloads > 0:
        print(warning(f"\nDownload completed with {failedDownloads} failures."))
    else:
        print(error("\nNo new downloads completed."))
    
    return {
        "total": totalClips,
        "success": successfulDownloads,
        "skipped": alreadyDownloaded,
        "failed": failedDownloads,
        "sizeMb": totalSizeMb
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        word = sys.argv[1].lower().strip()
        downloadWordVideos(word)
    else:
        # word = input("Enter the word to download videos for: ").strip().lower()
        word = "nuance"
        if word:
            downloadWordVideos(word)
        else:
            print(error("No word provided. Exiting."))
