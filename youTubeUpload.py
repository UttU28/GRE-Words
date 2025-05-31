#!/usr/bin/env python3
import os
import sys
import subprocess
import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

# Import common utilities
from utils import success, error, info, warning, highlight
from config import (
    INS_CHROME_DATA_DIR, DEBUGGING_PORT, CHROME_PATH as CONFIG_CHROME_PATH,
    FINAL_VIDEOS_DIR, pathStr, ensureDirsExist
)

# Only import pyautogui on Windows
if os.name == "nt":
    import pyautogui

# Set up logging
log_file = "youtube_upload.log"
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger('youtube_uploader')

# Path to the specific chromedriver (same as Instagram)
CHROMEDRIVER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                               'resources', 'chromedriver')

def getChromePath():
    if CONFIG_CHROME_PATH and os.path.exists(CONFIG_CHROME_PATH):
        return CONFIG_CHROME_PATH

    if os.name == "nt":
        chromePath = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        if not os.path.exists(chromePath):
            chromePath = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
    else:
        chromePath = "/usr/bin/google-chrome"
        if not os.path.exists(chromePath):
            chromePath = "/usr/bin/google-chrome-stable"
        if not os.path.exists(chromePath):
            chromePath = "/snap/bin/chromium"
        if not os.path.exists(chromePath):
            try:
                chromePath = subprocess.check_output(["which", "google-chrome"], text=True).strip()
            except subprocess.CalledProcessError:
                try:
                    chromePath = subprocess.check_output(["which", "chrome"], text=True).strip()
                except subprocess.CalledProcessError:
                    print(error("Chrome executable not found. Please install Chrome."))
                    sys.exit(1)
    
    return chromePath

def getVideoPath(word):
    capitalizedWord = word[0].upper() + word[1:]
    videoPath = os.path.join(pathStr(FINAL_VIDEOS_DIR), capitalizedWord + ".mp4")
    
    if not os.path.exists(videoPath):
        print(error(f"❌ Video not found: {capitalizedWord}.mp4"))
        return None
    return videoPath

def fillTitleAndDescription(driver, title, description):
    try:
        print(info("📝 Setting title and description..."))
        
        # Handle Title with robust typing like Instagram
        titleField = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#textbox[contenteditable='true'][role='textbox']"))
        )
        
        titleField.click()
        time.sleep(0.5)
        
        # Clear title field with multiple fallback methods
        try:
            titleField.send_keys(Keys.CONTROL + "a")
            titleField.send_keys(Keys.DELETE)
        except AttributeError:
            # Fallback 1: Try using ActionChains for Ctrl+A
            try:
                actions = ActionChains(driver)
                actions.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).perform()
                titleField.send_keys(Keys.DELETE)
            except:
                # Fallback 2: Use JavaScript to clear
                driver.execute_script("arguments[0].innerText = ''", titleField)
        
        time.sleep(0.5)
        
        # Try chunked typing for title (like Instagram)
        try:
            chunk_size = 20
            for i in range(0, len(title), chunk_size):
                chunk = title[i:i+chunk_size]
                titleField.send_keys(chunk)
                time.sleep(0.3)  # Small pause between chunks
        except Exception:
            # Fallback: Use JavaScript to set title
            try:
                driver.execute_script("arguments[0].innerText = arguments[1]", titleField, title)
            except Exception:
                titleField.send_keys(title)  # Last resort
        
        print(success("✅ Title set"))
        
        # Handle Description with robust typing like Instagram
        descriptionSelectors = [
            "ytcp-social-suggestions-textbox[label='Description'] #textbox[contenteditable='true']",
            "#description-textarea #textbox[contenteditable='true']",
            "div[aria-label*='Tell viewers about your video'][contenteditable='true']"
        ]
        
        descriptionField = None
        for selector in descriptionSelectors:
            try:
                descriptionField = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                break
            except:
                continue
        
        if descriptionField:
            descriptionField.click()
            time.sleep(0.5)
            
            # Clear description field with multiple fallback methods
            try:
                descriptionField.send_keys(Keys.CONTROL + "a")
                descriptionField.send_keys(Keys.DELETE)
            except AttributeError:
                # Fallback 1: Try using ActionChains for Ctrl+A
                try:
                    actions = ActionChains(driver)
                    actions.key_down(Keys.CONTROL).send_keys("a").key_up(Keys.CONTROL).perform()
                    descriptionField.send_keys(Keys.DELETE)
                except:
                    # Fallback 2: Use JavaScript to clear
                    driver.execute_script("arguments[0].innerText = ''", descriptionField)
            
            time.sleep(0.5)
            
            # Try chunked typing for description (like Instagram)
            try:
                chunk_size = 50
                for i in range(0, len(description), chunk_size):
                    chunk = description[i:i+chunk_size]
                    descriptionField.send_keys(chunk)
                    time.sleep(0.5)  # Small pause between chunks
                print(success("✅ Description set"))
            except Exception:
                # Fallback 1: Try alternative selector
                try:
                    descriptionField = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[@contenteditable='true' and @aria-label]"))
                    )
                    descriptionField.click()
                    time.sleep(0.5)
                    
                    # Try chunked typing again
                    chunk_size = 50
                    for i in range(0, len(description), chunk_size):
                        chunk = description[i:i+chunk_size]
                        descriptionField.send_keys(chunk)
                        time.sleep(0.5)
                    print(success("✅ Description set (alternative method)"))
                except Exception:
                    # Fallback 2: Use JavaScript to set description
                    try:
                        driver.execute_script("arguments[0].innerText = arguments[1]", descriptionField, description)
                        print(success("✅ Description set (JavaScript method)"))
                    except Exception:
                        # Fallback 3: Try to set description in smaller chunks with JavaScript
                        try:
                            driver.execute_script("arguments[0].innerText = ''", descriptionField)
                            chunk_size = 50
                            for i in range(0, len(description), chunk_size):
                                chunk = description[i:i+chunk_size]
                                current = driver.execute_script("return arguments[0].innerText", descriptionField)
                                driver.execute_script("arguments[0].innerText = arguments[1]", descriptionField, current + chunk)
                                time.sleep(0.5)
                            print(success("✅ Description set (JavaScript chunked method)"))
                        except Exception:
                            print(warning("⚠️ Could not set description"))
        else:
            print(warning("⚠️ Description field not found"))
        
        print(success("✅ Title and description configuration completed"))
        
    except Exception as e:
        print(error(f"❌ Error setting title/description: {e}"))

def selectFirstPlaylist(driver):
    try:
        print(info("📁 Selecting playlist..."))
        
        playlistSelectors = [
            "ytcp-dropdown-trigger[aria-label*='Select playlists']",
            "ytcp-dropdown-trigger[aria-label*='Select']",
            "ytcp-text-dropdown-trigger"
        ]
        
        playlistDropdown = None
        for selector in playlistSelectors:
            try:
                playlistDropdown = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                break
            except:
                continue
        
        if playlistDropdown:
            playlistDropdown.click()
            time.sleep(2)
            
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "tp-yt-paper-dialog[aria-label='Choose playlists']"))
                )
                
                firstCheckbox = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "#checkbox-0, ytcp-checkbox-lit[id='checkbox-0']"))
                )
                firstCheckbox.click()
                
                doneButton = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "ytcp-button.done-button"))
                )
                doneButton.click()
                print(success("✅ Playlist selected"))
                
            except Exception:
                print(warning("⚠️ Playlist selection failed"))
                try:
                    closeButton = driver.find_element(By.CSS_SELECTOR, "ytcp-button.done-button")
                    closeButton.click()
                except:
                    pass
        
    except Exception as e:
        print(error(f"❌ Playlist error: {e}"))

def setNotMadeForKids(driver):
    try:
        print(info("👶 Setting audience..."))
        
        notForKidsRadio = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']"))
        )
        notForKidsRadio.click()
        print(success("✅ Set as not for kids"))
        
    except Exception as e:
        print(error(f"❌ Audience setting error: {e}"))

def expandAdvancedOptions(driver):
    try:
        print(info("🔽 Expanding options..."))
        
        showMoreSelectors = [
            "ytcp-button[aria-label*='Show advanced settings']",
            "#toggle-button"
        ]
        
        showMoreButton = None
        for selector in showMoreSelectors:
            try:
                if selector == "#toggle-button":
                    showMoreButton = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                else:
                    xpathSelector = "//ytcp-button[.//div[contains(text(), 'Show more')]]"
                    showMoreButton = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, xpathSelector))
                    )
                break
            except:
                continue
        
        if showMoreButton:
            showMoreButton.click()
            time.sleep(2)
            print(success("✅ Options expanded"))
        
    except Exception as e:
        print(error(f"❌ Expand options error: {e}"))

def addTags(driver, tags):
    try:
        print(info("🏷️ Adding tags..."))
        
        tagsInput = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#text-input[aria-label='Tags']"))
        )
        tagsInput.click()
        time.sleep(0.5)
        
        # Try chunked typing for tags (like Instagram)
        try:
            chunk_size = 30
            for i in range(0, len(tags), chunk_size):
                chunk = tags[i:i+chunk_size]
                tagsInput.send_keys(chunk)
                time.sleep(0.3)  # Small pause between chunks
            print(success("✅ Tags added"))
        except Exception:
            # Fallback: Use JavaScript to set tags
            try:
                driver.execute_script("arguments[0].value = arguments[1]", tagsInput, tags)
                print(success("✅ Tags added (JavaScript method)"))
            except Exception:
                # Last resort: simple send_keys
                tagsInput.send_keys(tags)
                print(success("✅ Tags added (simple method)"))
        
    except Exception as e:
        print(error(f"❌ Tags error: {e}"))

def setCategoryToEntertainment(driver):
    try:
        print(info("🎭 Setting category..."))
        
        categoryDropdown = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#category ytcp-dropdown-trigger"))
        )
        categoryDropdown.click()
        time.sleep(2)
        
        entertainmentSelectors = [
            "tp-yt-paper-item[test-id='CREATOR_VIDEO_CATEGORY_ENTERTAINMENT']",
            "#text-item-3"
        ]
        
        entertainmentOption = None
        for selector in entertainmentSelectors:
            try:
                entertainmentOption = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
                break
            except:
                continue
        
        if not entertainmentOption:
            xpathSelector = "//tp-yt-paper-item[.//yt-formatted-string[text()='Entertainment']]"
            entertainmentOption = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, xpathSelector))
            )
        
        entertainmentOption.click()
        print(success("✅ Category set to Entertainment"))
        
    except Exception as e:
        print(error(f"❌ Category error: {e}"))

def clickNextButton(driver):
    try:
        print(info("➡️ Next step..."))
        
        nextButton = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#next-button"))
        )
        nextButton.click()
        time.sleep(3)
        print(success("✅ Proceeded"))
        
    except Exception as e:
        print(error(f"❌ Next button error: {e}"))

def setPublicAndSave(driver):
    try:
        print(info("🌍 Publishing..."))
        
        publicRadio = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "tp-yt-paper-radio-button[name='PUBLIC']"))
        )
        publicRadio.click()
        time.sleep(2)
        
        saveButton = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#done-button"))
        )
        saveButton.click()
        print(success("✅ Video published"))
        return True
        
    except Exception as e:
        print(error(f"❌ Publishing error: {e}"))
        return False
    
def handleFileUpload(driver, videoPath):
    """Handle file upload for Windows using pyautogui"""
    try:
        pyautogui.typewrite(videoPath, interval=0.05)
        time.sleep(0.5)
        pyautogui.press('enter')
        print(success("✅ File selected (Windows)"))
    except Exception as e:
        print(error(f"❌ File upload error: {e}"))
        raise

def clickCreateAndUpload(driver, word):
    try:
        createButton = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "ytcp-button#create-icon"))
        )
        createButton.click()
        
        uploadOption = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "tp-yt-paper-item[test-id='upload-beta']"))
        )
        uploadOption.click()
        
        videoPath = getVideoPath(word)
        if videoPath:
            print(info(f"📁 Uploading {os.path.basename(videoPath)}..."))
            
            if os.name == "nt":
                # Windows: Click the select files button and use pyautogui
                selectFilesButton = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "#select-files-button"))
                )
                selectFilesButton.click()
                time.sleep(2)
                handleFileUpload(driver, videoPath)
            else:
                # Ubuntu: Find the hidden file input and send file path directly (like Instagram)
                time.sleep(2)
                try:
                    uploadInput = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
                    )
                    uploadInput.send_keys(videoPath)
                    print(success(f"✅ File selected (Ubuntu method): {os.path.basename(videoPath)}"))
                except Exception as e:
                    print(error(f"Could not find file input to upload video: {e}"))
                    raise
            
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ytcp-video-metadata-editor"))
            )
            print(success("✅ Upload started"))
        
    except Exception as e:
        print(error(f"❌ Upload initiation error: {e}"))

def uploadToYoutube(word, caption):
    start_time = time.time()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        print(highlight(f"\n=== YouTube Upload Started for {word.upper()} ==="))
        logger.info(f"Starting YouTube upload for word: {word}")
        logger.info(f"Caption: {caption}")
        
        ensureDirsExist()
        
        title = f"{word.upper()}"
        # Create the same hashtag string as used in Instagram
        instagram_hashtags_string = "#GREprep #IELTSvocab #wordoftheday #englishwithstyle #speaklikeanative #studygram #vocabularyboost #learnenglish #englishreels #explorepage #IELTSpreparation #englishvocabulary #spokenenglish #studymotivation #englishlearning #dailyvocab #englishpractice #fluencygoals #vocabchallenge #englishtips #educationreels #englishgrammar #ieltsvocab #smartvocab"
        
        description = f"{word.upper()}\n\n{caption}\n\n{instagram_hashtags_string}"
        tags = "GRE, IELTS, vocabulary, english, learning, education, words, study, exam prep, english vocabulary"
        
        chromePath = getChromePath()
        url = 'https://studio.youtube.com/channel/UCHvf5d1izlR4MR786HJzoew'
        userDataDir = pathStr(INS_CHROME_DATA_DIR)
        
        osName = "Windows" if os.name == "nt" else "Ubuntu"
        print(highlight(f"🚀 YouTube Upload - {word.upper()} ({osName})"))
        print(info("="*50))
        
        chromeArgs = [
            chromePath,
            f"--remote-debugging-port={DEBUGGING_PORT}",
            f"--user-data-dir={userDataDir}",
            "--disable-notifications",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-blink-features=AutomationControlled",
            url
        ]
        
        chromeProcess = subprocess.Popen(chromeArgs)
        time.sleep(2)
        
        chromeOptions = Options()
        chromeOptions.add_experimental_option("debuggerAddress", f"localhost:{DEBUGGING_PORT}")
        
        # Use the specific chromedriver (same as Instagram)
        service = Service(executable_path=CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=chromeOptions)
        
        print(success(f"✅ Connected to Chrome ({osName})"))
        
        clickCreateAndUpload(driver, word)
        
        print(info("📋 Configuring video..."))
        fillTitleAndDescription(driver, title, description)
        selectFirstPlaylist(driver)
        setNotMadeForKids(driver)
        expandAdvancedOptions(driver)
        addTags(driver, tags)
        setCategoryToEntertainment(driver)
        
        print(info("🔄 Processing..."))
        clickNextButton(driver)
        clickNextButton(driver)
        clickNextButton(driver)
        
        time.sleep(3)
        
        uploadSuccess = setPublicAndSave(driver)
        time.sleep(10)
        
        print(info("="*50))
        if uploadSuccess:
            print(success("🎉 YouTube Upload Complete!"))
        else:
            print(error("❌ Upload Failed"))
        print(info("="*50))
        
        # Close Chrome session
        try:
            driver.quit()
            print(info("🔒 Closing Chrome session..."))
            chromeProcess.terminate()
            chromeProcess.wait(timeout=5)
            print(success("✅ Chrome session closed"))
        except Exception as e:
            print(warning(f"⚠️ Error closing Chrome: {e}"))
            try:
                chromeProcess.kill()
            except:
                pass
        
        end_time = time.time()
        duration = end_time - start_time
        minutes = int(duration // 60)
        seconds = int(duration % 60)
        
        if uploadSuccess:
            print(success(f"YouTube upload completed successfully in {minutes}m {seconds}s"))
            logger.info(f"YouTube upload successful for {word}. Duration: {minutes}m {seconds}s")
            return True
        else:
            print(error(f"YouTube upload failed for {word}"))
            logger.error(f"YouTube upload failed for {word}")
            return False
        
    except Exception as e:
        print(error(f"❌ YouTube upload error: {e}"))
        logger.error(f"Error during YouTube upload: {e}")
        # Cleanup on error
        try:
            if 'driver' in locals():
                driver.quit()
            if 'chromeProcess' in locals():
                chromeProcess.terminate()
                chromeProcess.wait(timeout=5)
        except:
            try:
                if 'chromeProcess' in locals():
                    chromeProcess.kill()
            except:
                pass
        return False


def main():
    word = "Balk"
    caption = "BALK means to hesitate or refuse to proceed; to stop short and refuse to continue."
    
    result = uploadToYoutube(word, caption)
    print(success("✅ Success") if result else error("❌ Failed"))

if __name__ == "__main__":
    main()
