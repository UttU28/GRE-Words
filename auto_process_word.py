import os
import json
import random
import sys
import time

# Import functions from other scripts
from config import JSON_FILE, path_str, ensure_dirs_exist
# Import functions from the specific modules (adjust path as needed)
import importlib.util

def import_from_file(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Import functions from each script
downloads_module = import_from_file("downloadingVideos", "2_downloadingVideos.py")
images_module = import_from_file("makeImages", "3_makeImages.py")
add_video_module = import_from_file("addVideoToImage", "4_addVideoToImage.py")
merge_module = import_from_file("mergeAllOneByOne", "5_mergeAllOneByOne.py")

# Get functions from modules
download_word_videos = downloads_module.download_word_videos
make_images_for_word = images_module.make_images_for_word
process_word = add_video_module.process_word
merge_word_videos = merge_module.merge_word_videos

def select_random_word():
    """Select a random word from the JSON file that hasn't been processed yet"""
    try:
        with open(path_str(JSON_FILE), "r") as file:
            data = json.load(file)
        
        # Filter words that have been searched but not used yet
        eligible_words = [
            word for word, word_data in data.items() 
            if word_data.get("searched", False) and 
            word_data.get("clipsFound", 0) > 0 and
            not word_data.get("wordUsed", False)
        ]
        
        if not eligible_words:
            print("No eligible words found. All words have been processed or have no clips.")
            return None
        
        selected_word = random.choice(eligible_words)
        print(f"Randomly selected word: {selected_word.upper()}")
        return selected_word
        
    except Exception as e:
        print(f"Error selecting random word: {e}")
        return None

def process_complete_word(word=None):
    """Process a word through all scripts from start to finish"""
    start_time = time.time()
    
    # If no word is provided, select a random one
    if not word:
        word = select_random_word()
        if not word:
            return False
    
    print(f"\n{'='*60}")
    print(f"Starting complete processing for word: {word.upper()}")
    print(f"{'='*60}\n")
    
    # Step 1: Download videos
    print(f"\n--- STEP 1: Downloading videos for {word} ---")
    download_result = download_word_videos(word)
    if not download_result or download_result.get("success", 0) + download_result.get("skipped", 0) == 0:
        print(f"Failed to download any videos for {word}. Aborting.")
        return False
    
    # Step 2: Create images for each clip
    print(f"\n--- STEP 2: Generating images for {word} ---")
    image_result = make_images_for_word(word)
    if not image_result:
        print(f"Failed to create images for {word}. Aborting.")
        return False
    
    # Step 3: Add video to images
    print(f"\n--- STEP 3: Adding videos to images for {word} ---")
    merge_result = process_word(word)
    if not merge_result:
        print(f"Failed to add videos to images for {word}. Aborting.")
        return False
    
    # Step 4: Create final video
    print(f"\n--- STEP 4: Creating final video for {word} ---")
    final_result = merge_word_videos(word)
    if not final_result:
        print(f"Failed to create final video for {word}. Aborting.")
        return False
    
    # Update word status
    try:
        with open(path_str(JSON_FILE), "r") as file:
            data = json.load(file)
        
        if word in data:
            data[word]["wordUsed"] = True
            data[word]["completedDate"] = time.strftime("%Y-%m-%d %H:%M:%S")
            
            with open(path_str(JSON_FILE), "w") as file:
                json.dump(data, file, indent=2)
    except Exception as e:
        print(f"Error updating word status: {e}")
    
    # Calculate total time
    end_time = time.time()
    total_time = end_time - start_time
    minutes = int(total_time // 60)
    seconds = int(total_time % 60)
    
    print(f"\n{'='*60}")
    print(f"COMPLETE PROCESSING FOR {word.upper()} FINISHED SUCCESSFULLY!")
    print(f"Total time: {minutes} minutes {seconds} seconds")
    print(f"{'='*60}\n")
    
    return True

def process_batch(count=5, max_failures=10):
    """Process a batch of random words"""
    print(f"Starting batch processing of up to {count} words")
    
    successful = 0
    failures = 0
    
    while successful < count and failures < max_failures:
        print(f"\nProcessing word {successful+1} of {count}")
        
        if process_complete_word():
            successful += 1
        else:
            failures += 1
            print(f"Failed to process word. Failures: {failures}/{max_failures}")
            
            # If too many failures, break
            if failures >= max_failures:
                print(f"Reached maximum failure count ({max_failures}). Stopping batch processing.")
                break
                
            # Wait a bit before trying the next word
            time.sleep(2)
    
    print(f"\nBatch processing complete.")
    print(f"Successfully processed: {successful} words")
    print(f"Failed to process: {failures} words")
    
    return successful, failures

if __name__ == "__main__":
    # Ensure all directories exist
    ensure_dirs_exist()
    
    # Check arguments
    if len(sys.argv) > 1:
        if sys.argv[1].lower() == "batch":
            # Process a batch with optional count parameter
            batch_size = 5  # Default batch size
            if len(sys.argv) > 2 and sys.argv[2].isdigit():
                batch_size = int(sys.argv[2])
            
            max_failures = 10  # Default max failures
            if len(sys.argv) > 3 and sys.argv[3].isdigit():
                max_failures = int(sys.argv[3])
                
            process_batch(batch_size, max_failures)
        elif sys.argv[1].isdigit():
            # If a number is provided, process that many random words
            count = int(sys.argv[1])
            print(f"Processing {count} random words")
            
            successful = 0
            for i in range(count):
                print(f"\nProcessing word {i+1} of {count}")
                if process_complete_word():
                    successful += 1
                else:
                    print("Failed to process word, moving to next one")
            
            print(f"\nCompleted processing {successful} out of {count} words successfully")
        else:
            # Process a specific word
            word = sys.argv[1].lower().strip()
            process_complete_word(word)
    else:
        # Process a single random word
        process_complete_word()
        
    print("\nScript execution complete.") 