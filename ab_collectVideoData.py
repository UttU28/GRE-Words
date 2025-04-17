from time import sleep
import time
import subprocess
import os
import json
import sys
import random
import re
import traceback
from datetime import datetime
import asyncio
import threading
import signal
import platform
from multiprocessing import Process, Queue
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from config import JSON_FILE, SCR_CHROME_DATA_DIR, DEBUGGING_PORT, pathStr, ensureDirsExist

ensureDirsExist()

USER_DATA_DIR = pathStr(SCR_CHROME_DATA_DIR)

if platform.system() == "Windows":
    CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    if not os.path.exists(CHROME_PATH):
        CHROME_PATH = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
        if not os.path.exists(CHROME_PATH):
            localAppData = os.environ.get('LOCALAPPDATA', '')
            possiblePath = os.path.join(localAppData, "Google\\Chrome\\Application\\chrome.exe")
            if os.path.exists(possiblePath):
                CHROME_PATH = possiblePath
else:
    CHROME_PATH = "/usr/bin/google-chrome"
    if not os.path.exists(CHROME_PATH):
        CHROME_PATH = "/usr/bin/google-chrome-stable"
    if not os.path.exists(CHROME_PATH):
        CHROME_PATH = "/snap/bin/chromium"
    if not os.path.exists(CHROME_PATH):
        try:
            CHROME_PATH = subprocess.check_output(["which", "google-chrome"], text=True).strip()
        except subprocess.CalledProcessError:
            try:
                CHROME_PATH = subprocess.check_output(["which", "chrome"], text=True).strip()
            except subprocess.CalledProcessError:
                print("Chrome executable not found. Please install Chrome or specify its path.")
                print("You can set the CHROME_PATH in the .env file.")
                sys.exit(1)

if not os.path.exists(CHROME_PATH):
    print(f"Error: Chrome executable not found at {CHROME_PATH}")
    print("Please ensure Chrome is installed or provide the correct path in your .env file.")
    sys.exit(1)

print(f"Chrome executable path: {CHROME_PATH}")

def load_json_data():
    """Load the JSON data from file"""
    try:
        with open(pathStr(JSON_FILE), "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"JSON file not found at {pathStr(JSON_FILE)}. Creating a new one.")
        return {}
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {pathStr(JSON_FILE)}. Creating a new one.")
        return {}

def save_json_data(data):
    """Save the JSON data to file"""
    with open(pathStr(JSON_FILE), "w") as file:
        json.dump(data, file, indent=2)
    print("Data saved to JSON file")

# Load the JSON data
data = load_json_data()

def start_chrome_session():
    """Start Chrome browser and connect to it with Selenium"""
    print("Starting Chrome browser...")
    
    chrome_process = subprocess.Popen([
        CHROME_PATH,
        f"--remote-debugging-port={DEBUGGING_PORT}",
        f"--user-data-dir={USER_DATA_DIR}",
        "--disable-notifications",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-blink-features=AutomationControlled"
    ])
    
    sleep(1)
    
    options = Options()
    options.add_experimental_option("debuggerAddress", f"localhost:{DEBUGGING_PORT}")
    
    driver = webdriver.Chrome(options=options)
    
    return driver, chrome_process

def cleanup_chrome(driver, chrome_process):
    """Close Chrome browser and clean up processes"""
    print("Cleaning up Chrome session on port", DEBUGGING_PORT)
    
    try:
        if driver:
            driver.quit()
    except Exception as e:
        print(f"Error quitting driver: {e}")
    
    try:
        if chrome_process:
            chrome_process.terminate()
            chrome_process.wait(timeout=5)
    except Exception as e:
        print(f"Error terminating Chrome process: {e}")
        try:
            if chrome_process:
                chrome_process.kill()
        except:
            pass

def process_word(driver, word):
    """Process a single word and collect its clips"""
    print(f"Processing word: {word}")
    
    # Ensure the word exists in the data structure
    if word not in data:
        data[word] = {
            "searched": False,
            "clipsFound": 0,
            "clipData": {}
        }
    
    try:
        driver.get(f"https://www.playphrase.me/#/search?q={word}")
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "app")) and 
            EC.presence_of_element_located((By.CLASS_NAME, "video-player-container"))
        )
        
        actions = ActionChains(driver)
        
        for pos in range(10):
            print(f"Processing clip position {pos}")
            
            try:
                sleep(2)
                
                current_url = driver.current_url
                
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "video-player-container"))
                )
                
                videoData = element.find_element(By.TAG_NAME, "video")
                videoURL = videoData.get_attribute("src")

                subtitleData = element.find_elements(By.CLASS_NAME, "s-word")
                subtitle = " ".join([subtitle.text for subtitle in subtitleData])

                videoInfoData = driver.find_elements(By.CLASS_NAME, "overlay-video-info")
                videoInfo = "N/A"
                for info in videoInfoData:
                    if info.text.strip() != "Download video":
                        videoInfo = info.text.strip()
                        break

                currentIndex = pos + 1
                
                data[word]["clipData"][str(currentIndex)] = {
                    "videoURL": videoURL, 
                    "subtitle": subtitle, 
                    "videoInfo": videoInfo
                }
                
                print(f"  Successfully saved clip {currentIndex}")
                
                # Save progress after each clip
                save_json_data(data)
                
                if pos < 9:
                    element.click()
                    sleep(0.5)
                    actions.send_keys(Keys.ARROW_DOWN).perform()
                    sleep(2)
                    
                    new_url = driver.current_url
                    if current_url == new_url:
                        print("  No more clips available (position didn't change)")
                        break
                    
                    try:
                        new_video = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.TAG_NAME, "video"))
                        )
                        new_url = new_video.get_attribute("src")
                        if new_url == videoURL:
                            print("  No new video loaded, likely at the end of available clips")
                            break
                    except Exception as e:
                        print(f"  Could not verify new video loaded: {e}")
                        break
                
            except Exception as e:
                print(f"  Error processing clip at position {pos}: {e}")
                break
        
        data[word]["searched"] = True
        data[word]["clipsFound"] = len(data[word]["clipData"])
        
        print(f"Completed processing '{word}'. Found {data[word]['clipsFound']} clips.")
        return True
        
    except Exception as e:
        print(f"Error processing word '{word}': {e}")
        return False

def get_unsearched_words():
    """Get a list of words that haven't been searched yet"""
    return [word for word, wordData in data.items() if not wordData.get("searched", False)]

def main():
    # Initialize driver and chrome_process as None to avoid NameError in finally block
    driver = None
    chrome_process = None

    try:
        driver, chrome_process = start_chrome_session()
        driver.maximize_window()
        
        driver.get("https://www.google.com")
        sleep(2)
        
        words_processed = 0
        consecutive_no_clips = 0  # Counter for consecutive words with no clips
        
        unsearched_words = get_unsearched_words()
        
        if not unsearched_words:
            print("No unsearched words found in the JSON data. Please add words to search.")
            return
            
        print(f"Found {len(unsearched_words)} unsearched words.")
        
        for currentWord in unsearched_words:
            print(f"\n{'='*50}\nProcessing word #{words_processed+1}: {currentWord}\n{'='*50}")
            
            success = process_word(driver, currentWord)
            words_processed += 1
            
            save_json_data(data)
            
            print(f"Data saved for '{currentWord}'")
            
            # Check if we found any clips for this word
            if data[currentWord]["clipsFound"] == 0:
                consecutive_no_clips += 1
                print(f"Warning: No clips found for {consecutive_no_clips} consecutive words")
                if consecutive_no_clips >= 5:
                    print(f"Stopping script: No clips found for {consecutive_no_clips} consecutive words")
                    break
            else:
                # Reset counter if we found clips
                consecutive_no_clips = 0
            
            print("Navigating to Google to reset for next word...")
            driver.get("https://www.google.com")
            sleep(2)
            
        print(f"Script completed. Processed {words_processed} words.")

    except Exception as e:
        print(f"Unhandled error: {e}")
        traceback.print_exc()
        
    finally:
        save_json_data(data)
        cleanup_chrome(driver, chrome_process)

if __name__ == "__main__":
    main()
            