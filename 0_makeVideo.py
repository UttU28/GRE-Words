import os
import random
import sys
import time
import shutil
from colorama import init, Fore, Style

from config import pathStr, ensureDirsExist, IMAGES_DIR, DOWNLOADED_VIDEOS_DIR, MERGED_VIDEOS_DIR
import importlib.util
from db_controller import db

# Initialize colorama
init(autoreset=True)

# Color formatting functions
def success(text): return f"{Fore.GREEN}{text}{Style.RESET_ALL}"
def error(text): return f"{Fore.RED}{text}{Style.RESET_ALL}"
def info(text): return f"{Fore.CYAN}{text}{Style.RESET_ALL}"
def warning(text): return f"{Fore.YELLOW}{text}{Style.RESET_ALL}"
def highlight(text): return f"{Fore.MAGENTA}{Style.BRIGHT}{text}{Style.RESET_ALL}"

def importFromFile(moduleName, filePath):
    spec = importlib.util.spec_from_file_location(moduleName, filePath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

downloadsModule = importFromFile("downloadingVideos", "1_downloadingVideos.py")
imagesModule = importFromFile("makeImages", "2_makeImages.py")
addVideoModule = importFromFile("addVideoToImage", "3_addVideoToImage.py")
introOutroModule = importFromFile("createIntroOutroVideos", "4_createIntroOutro.py")
mergeModule = importFromFile("mergeAllOneByOne", "5_mergeAllOneByOne.py")

downloadWordVideos = downloadsModule.downloadWordVideos
makeImagesForWord = imagesModule.makeImagesForWord
processWord = addVideoModule.processWord
createIntroOutroVideos = introOutroModule.createIntroOutroVideos
mergeWordVideos = mergeModule.mergeWordVideos

def selectRandomWord():
    """Select a random word from the database that hasn't been processed yet"""
    try:
        wordRow = db.getRandomWord()
        
        if not wordRow:
            print(error("No eligible words found. All words have been processed or have no clips."))
            return None
        
        selectedWord = wordRow['word']
        print(highlight(f"Randomly selected word: {selectedWord.upper()}"))
        return selectedWord
        
    except Exception as e:
        print(error(f"Error selecting random word: {e}"))
        return None

def cleanupTempFiles(word):
    """Clean up temporary files after processing is complete"""
    print(info(f"\n--- Cleaning up temporary files for {word} ---"))
    
    # Clean up all image files
    imagesDir = pathStr(IMAGES_DIR)
    imageCount = 0
    
    try:
        for filename in os.listdir(imagesDir):
            # Delete all images in the directory
            filePath = os.path.join(imagesDir, filename)
            if os.path.isfile(filePath):
                os.remove(filePath)
                imageCount += 1
        
        print(info(f"Removed {imageCount} image files from images directory"))
    except Exception as e:
        print(error(f"Error cleaning up image files: {e}"))
    
    # Clean up all downloaded videos
    downloadDir = pathStr(DOWNLOADED_VIDEOS_DIR)
    downloadCount = 0
    
    try:
        for filename in os.listdir(downloadDir):
            filePath = os.path.join(downloadDir, filename)
            if os.path.isfile(filePath):
                os.remove(filePath)
                downloadCount += 1
        
        print(info(f"Removed {downloadCount} video files from downloaded videos directory"))
    except Exception as e:
        print(error(f"Error cleaning up downloaded videos: {e}"))
    
    # Clean up all merged videos
    mergedDir = pathStr(MERGED_VIDEOS_DIR)
    mergedCount = 0
    
    try:
        for filename in os.listdir(mergedDir):
            filePath = os.path.join(mergedDir, filename)
            if os.path.isfile(filePath):
                os.remove(filePath)
                mergedCount += 1
        
        print(info(f"Removed {mergedCount} video files from merged videos directory"))
    except Exception as e:
        print(error(f"Error cleaning up merged videos: {e}"))
    
    print(success(f"Cleanup complete - all temporary files removed"))

def processCompleteWord(word=None):
    """Process a word through all scripts from start to finish"""
    startTime = time.time()
    
    if not word:
        word = selectRandomWord()
        if not word:
            return False
    
    # Get word data from database
    wordRow = db.getWord(word)
    if not wordRow:
        print(error(f"Word '{word}' not found in database"))
        return False
    
    wordId = wordRow['id']
    
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(highlight(f"Starting complete processing for word: {word.upper()}"))
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
    
    print(highlight(f"\n--- STEP 1: Downloading videos for {word.upper()} ---"))
    downloadResult = downloadWordVideos(word)
    if not downloadResult or downloadResult.get("success", 0) + downloadResult.get("skipped", 0) == 0:
        print(error(f"Failed to download any videos for {word}. Aborting."))
        return False
    
    print(highlight(f"\n--- STEP 2: Generating images for {word.upper()} ---"))
    imageResult = makeImagesForWord(word)
    if not imageResult:
        print(error(f"Failed to create images for {word}. Aborting."))
        return False
    
    print(highlight(f"\n--- STEP 3: Creating intro/outro images and videos for {word.upper()} ---"))
    introOutroResult = createIntroOutroVideos(word)
    if not introOutroResult:
        print(error(f"Failed to create intro/outro elements. Aborting."))
        return False
    
    print(highlight(f"\n--- STEP 4: Adding videos to images for {word.upper()} ---"))
    mergeResult = processWord(word)
    if not mergeResult:
        print(error(f"Failed to add videos to images for {word}. Aborting."))
        return False
    
    print(highlight(f"\n--- STEP 5: Creating final video for {word.upper()} ---"))
    finalResult = mergeWordVideos(word)
    if not finalResult:
        print(error(f"Failed to create final video for {word}. Aborting."))
        return False
    
    # Update database to mark word as processed
    completionTime = time.strftime("%Y-%m-%d %H:%M:%S")
    db.markWordAsProcessed(wordId)
    print(success(f"Updated database: marked '{word}' as processed at {completionTime}"))
    
    # Clean up temporary files
    cleanupTempFiles(word)
    
    endTime = time.time()
    totalTime = endTime - startTime
    minutes = int(totalTime // 60)
    seconds = int(totalTime % 60)
    
    print(f"\n{Fore.GREEN}{'='*60}{Style.RESET_ALL}")
    print(success(f"COMPLETE PROCESSING FOR {word.upper()} FINISHED SUCCESSFULLY!"))
    print(success(f"Total time: {minutes} minutes {seconds} seconds"))
    print(f"{Fore.GREEN}{'='*60}{Style.RESET_ALL}\n")
    
    print(info(f"File location: {os.path.abspath(__file__)}"))
    
    return True

def processBatch(count=5, maxFailures=10):
    """Process a batch of random words"""
    print(highlight(f"Starting batch processing of up to {count} words"))
    
    successful = 0
    failures = 0
    
    while successful < count and failures < maxFailures:
        print(info(f"\nProcessing word {successful+1} of {count}"))
        
        if processCompleteWord():
            successful += 1
        else:
            failures += 1
            print(warning(f"Failed to process word. Failures: {failures}/{maxFailures}"))
            
            if failures >= maxFailures:
                print(error(f"Reached maximum failure count ({maxFailures}). Stopping batch processing."))
                break
                
            time.sleep(2)
    
    print(info(f"\nBatch processing complete."))
    print(success(f"Successfully processed: {successful} words"))
    if failures > 0:
        print(warning(f"Failed to process: {failures} words"))
    
    return successful, failures

if __name__ == "__main__":
    ensureDirsExist()
    
    if len(sys.argv) > 1:
        if sys.argv[1].lower() == "batch":
            batchSize = 5
            if len(sys.argv) > 2 and sys.argv[2].isdigit():
                batchSize = int(sys.argv[2])
            
            maxFailures = 10
            if len(sys.argv) > 3 and sys.argv[3].isdigit():
                maxFailures = int(sys.argv[3])
                
            processBatch(batchSize, maxFailures)
        elif sys.argv[1].isdigit():
            count = int(sys.argv[1])
            print(highlight(f"Processing {count} random words"))
            
            successful = 0
            for i in range(count):
                print(info(f"\nProcessing word {i+1} of {count}"))
                if processCompleteWord():
                    successful += 1
                else:
                    print(warning("Failed to process word, moving to next one"))
            
            print(success(f"\nCompleted processing {successful} out of {count} words successfully"))
        else:
            word = sys.argv[1].lower().strip()
            processCompleteWord(word)
    else:
        processCompleteWord()
        