from time import sleep
import time
import subprocess
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from config import JSON_FILE, CHROME_DATA_DIR, DEBUGGING_PORT, path_str, ensure_dirs_exist

# Ensure necessary directories exist
ensure_dirs_exist()

# Configuration - use values from config
USER_DATA_DIR = path_str(CHROME_DATA_DIR)

# Determine Chrome path based on OS
if os.name == "nt":  # Windows
    CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    if not os.path.exists(CHROME_PATH):
        CHROME_PATH = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
else:  # Linux/Mac
    CHROME_PATH = "/usr/bin/google-chrome"

print(f"Chrome executable path: {CHROME_PATH}")

# Load JSON data from config path
with open(path_str(JSON_FILE), "r") as file:
    data = json.load(file)

def start_chrome_session():
    """Start Chrome browser and connect to it with Selenium"""
    print("Starting Chrome browser...")
    
    # Start Chrome process
    chrome_process = subprocess.Popen([
        CHROME_PATH,
        f"--remote-debugging-port={DEBUGGING_PORT}",
        f"--user-data-dir={USER_DATA_DIR}",
        "--disable-notifications",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-blink-features=AutomationControlled"
    ])
    
    # Give browser time to start
    sleep(2)
    
    # Set up Chrome options to connect to the running browser
    options = Options()
    options.add_experimental_option("debuggerAddress", f"localhost:{DEBUGGING_PORT}")
    
    # Create driver - simplified options to avoid errors
    driver = webdriver.Chrome(options=options)
    
    return driver, chrome_process

def cleanup_chrome(driver, chrome_process):
    """Close Chrome browser and clean up processes"""
    print("Cleaning up Chrome session on port", DEBUGGING_PORT)
    
    try:
        # Close and quit driver
        driver.quit()
    except Exception as e:
        print(f"Error quitting driver: {e}")
    
    try:
        # Terminate only the specific Chrome process we started
        chrome_process.terminate()
        chrome_process.wait(timeout=5)
    except Exception as e:
        print(f"Error terminating Chrome process: {e}")
        # Force kill if needed
        try:
            chrome_process.kill()
        except:
            pass
    
    # Do NOT use taskkill which would kill all Chrome instances

def process_word(driver, word):
    """Process a single word and collect its clips"""
    print(f"Processing word: {word}")
    
    try:
        # Navigate to the initial search page
        driver.get(f"https://www.playphrase.me/#/search?q={word}")
        
        # Wait for initial page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "app")) and 
            EC.presence_of_element_located((By.CLASS_NAME, "video-player-container"))
        )
        
        # Create ActionChains for keyboard control
        actions = ActionChains(driver)
        
        # Get up to 7 clips
        for pos in range(10):
            print(f"Processing clip position {pos}")
            
            try:
                # Wait a moment for the video to load
                sleep(2)
                
                # Get current video URL to check if position changes later
                current_url = driver.current_url
                
                # Ensure we have a video container
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "video-player-container"))
                )
                
                # Extract video data
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

                currentIndex = pos + 1  # Use 1-based indexing for the data storage
                
                # Save the data for this position
                data[word]["clipData"][str(currentIndex)] = {
                    "videoURL": videoURL, 
                    "subtitle": subtitle, 
                    "videoInfo": videoInfo
                }
                
                print(f"  Successfully saved clip {currentIndex}")
                
                # Press the down arrow to move to the next clip (if not the last one)
                if pos < 6:
                    # First click somewhere on the page to ensure focus
                    element.click()
                    sleep(0.5)
                    # Then send the down arrow key
                    actions.send_keys(Keys.ARROW_DOWN).perform()
                    sleep(2)  # Wait for the next clip to load
                    
                    # Check if URL/position actually changed
                    new_url = driver.current_url
                    if current_url == new_url:
                        print("  No more clips available (position didn't change)")
                        break
                
            except Exception as e:
                print(f"  Error processing clip at position {pos}: {e}")
                # If we can't process this position, we might be out of clips
                break
        
        # Mark as searched and update clip count
        data[word]["searched"] = True
        data[word]["clipsFound"] = len(data[word]["clipData"])
        
        print(f"Completed processing '{word}'. Found {data[word]['clipsFound']} clips.")
        return True
        
    except Exception as e:
        print(f"Error processing word '{word}': {e}")
        return False

try:
    # Start a single Chrome session for all words
    driver, chrome_process = start_chrome_session()
    driver.maximize_window()
    
    # Navigate to Google first
    driver.get("https://www.google.com")
    sleep(1)
    
    # Process all unsearched words
    words_processed = 0
    
    for currentWord, wordData in data.items():
        if not wordData["searched"]:
            print(f"\n{'='*50}\nProcessing word #{words_processed+1}: {currentWord}\n{'='*50}")
            
            success = process_word(driver, currentWord)
            words_processed += 1
            
            # Save data after each word to ensure it's not lost
            with open(path_str(JSON_FILE), "w") as file:
                json.dump(data, file, indent=2)
            
            print(f"Data saved for '{currentWord}'")
            
            # Navigate to Google after each word to reset state
            print("Navigating to Google to reset for next word...")
            driver.get("https://www.google.com")
            sleep(2)
            
            # Removed the break statement to process all words
    
    print(f"Script completed. Processed {words_processed} words.")

except Exception as e:
    print(f"Unhandled error: {e}")
    
finally:
    # Save data one last time just to be safe
    with open(path_str(JSON_FILE), "w") as file:
        json.dump(data, file, indent=2)
    
    # Clean up Chrome only at the end
    cleanup_chrome(driver, chrome_process)
            