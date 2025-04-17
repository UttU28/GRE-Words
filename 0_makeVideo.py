import os
import random
import time
import shutil
from colorama import init, Fore, Style

from config import pathStr, ensureDirsExist, IMAGES_DIR, DOWNLOADED_VIDEOS_DIR, MERGED_VIDEOS_DIR
import importlib.util
from db_controller import db

# Initialize colorama
init(autoreset=True)

# English vocabulary captions for Instagram posts
englishVocabCaptions = [
    "Just here to drop knowledge and vibes.",
    "Words hit different when you know what they mean.",
    "Fluent in English, sarcasm, and subtle shade.",
    "Reading books like it's a personality trait.",
    "My vibe is 50% grammar, 50% audacity.",
    "Learning new words to win petty arguments.",
    "If you can spell it, you can manifest it.",
    "More words, less worries.",
    "Not lost, just deep in a definition.",
    "Evolving my vocabulary one caption at a time.",
    
    "Talk wordy to me.",
    "Books before bros. Always.",
    "My sentences come with seasoning.",
    "Running on caffeine and compound words.",
    "I annotate vibes now.",
    "Every day is a vocab glow-up.",
    "Your favorite overthinker with a dictionary.",
    "Proof that nerdy is the new hot.",
    "Still processing the Oxford comma betrayal.",
    "Reading minds and metaphors.",
    
    "Lexicon locked and loaded.",
    "Living life one word of the day at a time.",
    "Overanalyzing everything since... always.",
    "Trying not to correct your grammar in public.",
    "Words are weapons. I'm fully armed.",
    "Mentally in a library. Physically? Here.",
    "Not a phase, just a lifelong love for adjectives.",
    "This post contains high levels of wordplay.",
    "Currently vibing with obscure synonyms.",
    "Inhale vocabulary, exhale wisdom.",
    
    "Making dictionaries look cool again.",
    "When in doubt, define it out.",
    "Vocabulary: leveled up.",
    "Grammar police, but fashion-forward.",
    "Linguistic flex, casual execution.",
    "Spelling it right just feels powerful.",
    "I'm not dramatic, I'm descriptively expressive.",
    "Manifesting main character diction.",
    "Reading is my cardio. Captions are my reps.",
    "My caption game? Autocorrect could never.",
    
    "Not just smart — syntactically smooth.",
    "This caption brought to you by brain cells and vibes.",
    "My favorite accessory? A metaphor.",
    "Trying to stay humble with a vocabulary like this.",
    "Diction: sharp. Fit: sharper.",
    "Loving myself like I love long words.",
    "Literally built different — like, with language.",
    "Word nerd? Nah, I'm a word artist.",
    "Being articulate is my superpower.",
    "Posting like punctuation depends on it."
]

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
uploadModule = importFromFile("uploadVideo", "6_uploadVideo.py")

downloadWordVideos = downloadsModule.downloadWordVideos
makeImagesForWord = imagesModule.makeImagesForWord
processWord = addVideoModule.processWord
createIntroOutroVideos = introOutroModule.createIntroOutroVideos
mergeWordVideos = mergeModule.mergeWordVideos
uploadVideo = uploadModule.main

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
    
    # Upload the final video to Instagram
    print(highlight(f"\n--- STEP 6: Uploading video to Instagram for {word.upper()} ---"))
    # Select a random caption from the list and append it to the word
    random_caption = random.choice(englishVocabCaptions)
    caption = f"{word.upper()}    {random_caption}"
    try:
        uploadResult = uploadVideo(word, caption)
        if uploadResult:
            print(success(f"Successfully uploaded video for {word} to Instagram"))
        else:
            print(warning(f"Failed to upload video for {word} to Instagram"))
    except Exception as e:
        print(error(f"Error uploading video to Instagram: {e}"))
    
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
    
    return True

if __name__ == "__main__":
    ensureDirsExist()
    processCompleteWord()
        