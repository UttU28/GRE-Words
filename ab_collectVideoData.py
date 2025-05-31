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
from utils import error, warning, info
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
                print("❌ Chrome executable not found. Please install Chrome or specify its path.")
                print("💡 You can set the CHROME_PATH in the .env file.")
                sys.exit(1)

if not os.path.exists(CHROME_PATH):
    print(error(f"❌ Chrome executable not found at {CHROME_PATH}"))
    print(error("💡 Please ensure Chrome is installed or provide the correct path in your .env file."))
    sys.exit(1)

print(f"🔍 Chrome executable: {CHROME_PATH}")

def loadJsonData():
    """Load the JSON data from file"""
    try:
        with open(pathStr(JSON_FILE), "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"📄 JSON file not found at {pathStr(JSON_FILE)}. Creating a new one.")
        return {}
    except json.JSONDecodeError:
        print(error(f"❌ Error decoding JSON from {pathStr(JSON_FILE)}. Creating a new one."))
        return {}

def saveJsonData(data):
    """Save the JSON data to file"""
    with open(pathStr(JSON_FILE), "w") as file:
        json.dump(data, file, indent=2)
    print("💾 Data saved to JSON file")

data = loadJsonData()

def startChromeSession():
    """Start Chrome browser and connect to it with Selenium"""
    print("🚀 Starting Chrome browser...")
    
    chromeProcess = subprocess.Popen([
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
    
    return driver, chromeProcess

def cleanupChrome(driver, chromeProcess):
    """Close Chrome browser and clean up processes"""
    print(f"🧹 Cleaning up Chrome session on port {DEBUGGING_PORT}")
    
    try:
        if driver:
            driver.quit()
    except Exception as e:
        print(error(f"❌ Error quitting driver: {e}"))
    
    try:
        if chromeProcess:
            chromeProcess.terminate()
            chromeProcess.wait(timeout=5)
    except Exception as e:
        print(error(f"❌ Error terminating Chrome process: {e}"))
        try:
            if chromeProcess:
                chromeProcess.kill()
        except:
            pass

def processWord(driver, word):
    """Process a single word and collect its clips"""
    print(f"🎯 Processing word: {word}")
    
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
            print(f"  📹 Processing clip position {pos}")
            
            try:
                sleep(2)
                
                currentUrl = driver.current_url
                
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
                
                print(f"    ✅ Saved clip {currentIndex}")
                
                saveJsonData(data)
                
                if pos < 9:
                    element.click()
                    sleep(0.5)
                    actions.send_keys(Keys.ARROW_DOWN).perform()
                    sleep(2)
                    
                    newUrl = driver.current_url
                    if currentUrl == newUrl:
                        print("    ⏹️  No more clips available")
                        break
                    
                    try:
                        newVideo = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.TAG_NAME, "video"))
                        )
                        newVideoUrl = newVideo.get_attribute("src")
                        if newVideoUrl == videoURL:
                            print("    ⏹️  End of available clips")
                            break
                    except Exception as e:
                        print(f"    ⚠️  Could not verify new video: {e}")
                        break
                
            except Exception as e:
                print(f"    ❌ Error at position {pos}: {e}")
                break
        
        data[word]["searched"] = True
        data[word]["clipsFound"] = len(data[word]["clipData"])
        
        print(f"✅ Completed '{word}' - Found {data[word]['clipsFound']} clips")
        return True
        
    except Exception as e:
        print(error(f"❌ Error processing '{word}': {e}"))
        return False

def getUnsearchedWords():
    """Get a list of words that haven't been searched yet"""
    return [word for word, wordData in data.items() if not wordData.get("searched", False)]

def main():
    driver = None
    chromeProcess = None

    try:
        driver, chromeProcess = startChromeSession()
        driver.maximize_window()
        
        driver.get("https://www.google.com")
        sleep(2)
        
        wordsProcessed = 0
        consecutiveNoClips = 0
        
        unsearchedWords = getUnsearchedWords()
        
        if not unsearchedWords:
            print("📭 No unsearched words found. Please add words to search.")
            return
            
        print(f"🎯 Found {len(unsearchedWords)} unsearched words")
        
        for currentWord in unsearchedWords:
            print(f"\n{'='*50}\n🔍 Word #{wordsProcessed+1}: {currentWord}\n{'='*50}")
            
            success = processWord(driver, currentWord)
            wordsProcessed += 1
            
            saveJsonData(data)
            
            print(f"💾 Data saved for '{currentWord}'")
            
            if data[currentWord]["clipsFound"] == 0:
                consecutiveNoClips += 1
                print(warning(f"⚠️  No clips found for {consecutiveNoClips} consecutive words"))
                if consecutiveNoClips >= 5:
                    print(f"🛑 Stopping: No clips found for {consecutiveNoClips} consecutive words")
                    break
            else:
                consecutiveNoClips = 0
            
            print("🔄 Resetting for next word...")
            driver.get("https://www.google.com")
            sleep(2)
            
        print(f"🎉 Script completed! Processed {wordsProcessed} words")

    except Exception as e:
        print(f"❌ Unhandled error: {e}")
        traceback.print_exc()
        
    finally:
        saveJsonData(data)
        cleanupChrome(driver, chromeProcess)

if __name__ == "__main__":
    main()
            