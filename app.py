import os
import random
import time
import shutil
import logging
from datetime import datetime, timedelta

# Import common utilities
from utils import success, error, info, warning, highlight, importFromFile
from config import pathStr, ensureDirsExist, IMAGES_DIR, DOWNLOADED_VIDEOS_DIR, MERGED_VIDEOS_DIR
from db_controller import db

# Set up logging
log_file = "word_processing.log"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('word_processor')

downloadsModule = importFromFile("downloadingVideos", "1_downloadingVideos.py")
imagesModule = importFromFile("makeImages", "2_makeImages.py")
addVideoModule = importFromFile("addVideoToImage", "3_addVideoToImage.py")
introOutroModule = importFromFile("createIntroOutroVideos", "4_createIntroOutro.py")
mergeModule = importFromFile("mergeAllOneByOne", "5_mergeAllOneByOne.py")
instagramUploadModule = importFromFile("instagramUpload", "instagramUpload.py")
youtubeUploadModule = importFromFile("youTubeUpload", "youTubeUpload.py")

downloadWordVideos = downloadsModule.downloadWordVideos
makeImagesForWord = imagesModule.makeImagesForWord
processWord = addVideoModule.processWord
createIntroOutroVideos = introOutroModule.createIntroOutroVideos
mergeWordVideos = mergeModule.mergeWordVideos
uploadToInstagram = instagramUploadModule.upload_to_instagram
uploadToYoutube = youtubeUploadModule.uploadToYoutube

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
    start_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if not word:
        word = selectRandomWord()
        if not word:
            logger.error(f"No eligible words found to process")
            return False
    
    # Log process start
    logger.info(f"STARTED processing word: {word.upper()} at {start_datetime}")
    
    # Get word data from database
    wordRow = db.getWord(word)
    if not wordRow:
        print(error(f"Word '{word}' not found in database"))
        logger.error(f"Word '{word}' not found in database")
        return False
    
    wordId = wordRow['id']
    
    print(f"\n{info('='*60)}")
    print(highlight(f"Starting complete processing for word: {word.upper()}"))
    print(f"{info('='*60)}\n")
    
    print(highlight(f"\n--- STEP 1: Downloading videos for {word.upper()} ---"))
    downloadResult = downloadWordVideos(word)
    if not downloadResult or downloadResult.get("success", 0) + downloadResult.get("skipped", 0) == 0:
        print(error(f"Failed to download any videos for {word}. Aborting."))
        logger.error(f"FAILED: Could not download any videos for {word}")
        return False
    
    print(highlight(f"\n--- STEP 2: Generating images for {word.upper()} ---"))
    imageResult = makeImagesForWord(word)
    if not imageResult:
        print(error(f"Failed to create images for {word}. Aborting."))
        logger.error(f"FAILED: Could not create images for {word}")
        return False
    
    print(highlight(f"\n--- STEP 3: Creating intro/outro images and videos for {word.upper()} ---"))
    introOutroResult = createIntroOutroVideos(word)
    if not introOutroResult:
        print(error(f"Failed to create intro/outro elements. Aborting."))
        logger.error(f"FAILED: Could not create intro/outro elements for {word}")
        return False
    
    print(highlight(f"\n--- STEP 4: Adding videos to images for {word.upper()} ---"))
    mergeResult = processWord(word)
    if not mergeResult:
        print(error(f"Failed to add videos to images for {word}. Aborting."))
        logger.error(f"FAILED: Could not add videos to images for {word}")
        return False
    
    print(highlight(f"\n--- STEP 5: Creating final video for {word.upper()} ---"))
    finalResult = mergeWordVideos(word)
    if not finalResult:
        print(error(f"Failed to create final video for {word}. Aborting."))
        logger.error(f"FAILED: Could not create final video for {word}")
        return False
    
    # Upload the final video to Instagram
    print(highlight(f"\n--- STEP 6: Uploading video to Instagram and YouTube for {word.upper()} ---"))
    
    # Get the meaning from the database
    meaning = wordRow.get('meaning', '')
    if not meaning:
        print(warning(f"No meaning found for {word} in database, using placeholder"))
        meaning = "a vocabulary word that enhances your English skills"
    
    # Create caption with meaning
    fixed_caption = """POV: You just unlocked a word that 99% still misuse  | If you're prepping for GRE, IELTS, or just wanna sound intellectually dangerous — SAVE THIS.  | Speak smarter, write sharper, and flex that vocab in style | Tag your study buddy | #GREprep #IELTSvocab #wordoftheday #englishwithstyle #speaklikeanative #studygram #vocabularyboost #learnenglish #englishreels #explorepage #IELTSpreparation #englishvocabulary #spokenenglish #studymotivation #englishlearning #dailyvocab #englishpractice #fluencygoals #vocabchallenge #englishtips #educationreels #englishgrammar #ieltsvocab #smartvocab"""
    caption = f"{word.upper()} means {meaning} ~ ~ ~ {fixed_caption}"
    
    uploadSuccess = False
    
    try:
        # Upload to YouTube
        print(highlight(f"\n--- Uploading to YouTube for {word.upper()} ---"))
        youtubeResult = uploadToYoutube(word, caption)
        if youtubeResult:
            print(success(f"Successfully uploaded video for {word} to YouTube"))
            logger.info(f"Successfully uploaded video for {word} to YouTube")
            uploadSuccess = True
        else:
            print(warning(f"Failed to upload video for {word} to YouTube"))
            logger.warning(f"Failed to upload video for {word} to YouTube")
            
        # Upload to Instagram
        print(highlight(f"\n--- Uploading to Instagram for {word.upper()} ---"))
        instagramResult = uploadToInstagram(word, caption)
        if instagramResult:
            print(success(f"Successfully uploaded video for {word} to Instagram"))
            uploadSuccess = True
            logger.info(f"Successfully uploaded video for {word} to Instagram")
        else:
            print(warning(f"Failed to upload video for {word} to Instagram"))
            logger.warning(f"Failed to upload video for {word} to Instagram")
            
            
    except Exception as e:
        print(error(f"Error uploading video: {e}"))
        logger.error(f"Error uploading video: {e}")
    
    # Update database to mark word as processed
    completionTime = time.strftime("%Y-%m-%d %H:%M:%S")
    db.markWordAsProcessed(wordId)
    print(success(f"Updated database: marked '{word}' as processed at {completionTime}"))
    logger.info(f"Updated database: marked '{word}' as processed at {completionTime}")
    
    # Clean up temporary files
    cleanupTempFiles(word)
    
    endTime = time.time()
    totalTime = endTime - startTime
    minutes = int(totalTime // 60)
    seconds = int(totalTime % 60)
    
    print(f"\n{success('='*60)}")
    print(success(f"COMPLETE PROCESSING FOR {word.upper()} FINISHED SUCCESSFULLY!"))
    print(success(f"Total time: {minutes} minutes {seconds} seconds"))
    print(f"{success('='*60)}\n")
    
    # Log process completion
    end_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logger.info(f"FINISHED processing word: {word.upper()} at {end_datetime}")
    logger.info(f"Total processing time: {minutes} minutes {seconds} seconds")
    logger.info(f"Overall status: {'SUCCESS' if uploadSuccess else 'PARTIAL SUCCESS (upload failed)'}")
    logger.info(f"{'-'*50}")
    
    return True

if __name__ == "__main__":
    ensureDirsExist()
    
    try:
        print(highlight("Starting continuous word processing cycle"))
        print(info("Pattern: Process word -> 11hr wait -> Process word -> Repeat"))
        
        while True:
            # Process a word
            print(highlight("\n=== Processing word ==="))
            processCompleteWord()
            
            # Sleep for 11 hours
            print(info(f"\nSleeping for 11 hours before next word..."))
            print(info(f"Next word will be processed at: {(datetime.now() + timedelta(hours=11)).strftime('%Y-%m-%d %H:%M:%S')}"))
            time.sleep(39600)  # 11 hours = 39600 seconds
            
    except KeyboardInterrupt:
        print(warning("\nProcess interrupted by user. Exiting..."))
    except Exception as e:
        print(error(f"\nAn error occurred in the main loop: {e}"))
        logger.error(f"Main loop error: {e}")
        