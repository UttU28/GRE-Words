#!/usr/bin/env python3
import os
import sys
import subprocess
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from colorama import init, Fore, Style
from config import (
    INS_CHROME_DATA_DIR, DEBUGGING_PORT, CHROME_PATH as CONFIG_CHROME_PATH,
    pathStr, FINAL_VIDEOS_DIR
)

# Only import pyautogui on Windows
if os.name == "nt":
    import pyautogui

# Initialize colorama
init(autoreset=True)

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
                    print(f"{Fore.RED}❌ Chrome not found")
                    sys.exit(1)
    
    return chromePath

def getVideoPath(word):
    capitalizedWord = word[0].upper() + word[1:]
    videoPath = os.path.join(pathStr(FINAL_VIDEOS_DIR), capitalizedWord + ".mp4")
    
    if not os.path.exists(videoPath):
        print(f"{Fore.RED}❌ Video not found: {capitalizedWord}.mp4")
        return None
    return videoPath

def fillTitleAndDescription(driver, title, description):
    try:
        print(f"{Fore.CYAN}📝 Setting title and description...")
        
        titleField = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#textbox[contenteditable='true'][role='textbox']"))
        )
        
        titleField.click()
        titleField.send_keys(Keys.CTRL + "a")
        titleField.send_keys(Keys.DELETE)
        time.sleep(0.5)
        titleField.send_keys(title)
        
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
            descriptionField.send_keys(Keys.CTRL + "a")
            descriptionField.send_keys(Keys.DELETE)
            time.sleep(0.5)
            descriptionField.send_keys(description)
            print(f"{Fore.GREEN}✅ Title and description set")
        else:
            print(f"{Fore.YELLOW}⚠️ Description field not found")
        
    except Exception as e:
        print(f"{Fore.RED}❌ Error setting title/description: {e}")

def selectFirstPlaylist(driver):
    try:
        print(f"{Fore.CYAN}📁 Selecting playlist...")
        
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
                print(f"{Fore.GREEN}✅ Playlist selected")
                
            except Exception:
                print(f"{Fore.YELLOW}⚠️ Playlist selection failed")
                try:
                    closeButton = driver.find_element(By.CSS_SELECTOR, "ytcp-button.done-button")
                    closeButton.click()
                except:
                    pass
        
    except Exception as e:
        print(f"{Fore.RED}❌ Playlist error: {e}")

def setNotMadeForKids(driver):
    try:
        print(f"{Fore.CYAN}👶 Setting audience...")
        
        notForKidsRadio = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "tp-yt-paper-radio-button[name='VIDEO_MADE_FOR_KIDS_NOT_MFK']"))
        )
        notForKidsRadio.click()
        print(f"{Fore.GREEN}✅ Set as not for kids")
        
    except Exception as e:
        print(f"{Fore.RED}❌ Audience setting error: {e}")

def expandAdvancedOptions(driver):
    try:
        print(f"{Fore.CYAN}🔽 Expanding options...")
        
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
            print(f"{Fore.GREEN}✅ Options expanded")
        
    except Exception as e:
        print(f"{Fore.RED}❌ Expand options error: {e}")

def addTags(driver, tags):
    try:
        print(f"{Fore.CYAN}🏷️ Adding tags...")
        
        tagsInput = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#text-input[aria-label='Tags']"))
        )
        tagsInput.click()
        time.sleep(0.5)
        tagsInput.send_keys(tags)
        print(f"{Fore.GREEN}✅ Tags added")
        
    except Exception as e:
        print(f"{Fore.RED}❌ Tags error: {e}")

def setCategoryToEntertainment(driver):
    try:
        print(f"{Fore.CYAN}🎭 Setting category...")
        
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
        print(f"{Fore.GREEN}✅ Category set to Entertainment")
        
    except Exception as e:
        print(f"{Fore.RED}❌ Category error: {e}")

def clickNextButton(driver):
    try:
        print(f"{Fore.CYAN}➡️ Next step...")
        
        nextButton = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#next-button"))
        )
        nextButton.click()
        time.sleep(3)
        print(f"{Fore.GREEN}✅ Proceeded")
        
    except Exception as e:
        print(f"{Fore.RED}❌ Next button error: {e}")

def setPublicAndSave(driver):
    try:
        print(f"{Fore.CYAN}🌍 Publishing...")
        
        publicRadio = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "tp-yt-paper-radio-button[name='PUBLIC']"))
        )
        publicRadio.click()
        time.sleep(2)
        
        saveButton = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#done-button"))
        )
        saveButton.click()
        print(f"{Fore.GREEN}✅ Video published")
        
    except Exception as e:
        print(f"{Fore.RED}❌ Publishing error: {e}")

def waitForUploadCompletion(driver):
    try:
        print(f"{Fore.CYAN}🔗 Waiting for completion...")
        
        shareDialog = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "tp-yt-paper-dialog[aria-labelledby='dialog-title']"))
        )
        
        shareUrlElement = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#share-url"))
        )
        
        videoUrl = shareUrlElement.get_attribute("href")
        print(f"{Fore.GREEN}🎉 Upload successful!")
        return True
        
    except Exception as e:
        print(f"{Fore.RED}❌ Upload completion error: {e}")
        return False

def handleFileUpload(driver, videoPath):
    try:
        if os.name == "nt":
            pyautogui.typewrite(videoPath, interval=0.05)
            time.sleep(0.5)
            pyautogui.press('enter')
            print(f"{Fore.GREEN}✅ File selected (Windows)")
        else:
            time.sleep(3)
            uploadInput = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
            )
            uploadInput.send_keys(videoPath)
            print(f"{Fore.GREEN}✅ File selected (Ubuntu)")
    except Exception as e:
        print(f"{Fore.RED}❌ File upload error: {e}")
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
        
        selectFilesButton = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#select-files-button"))
        )
        selectFilesButton.click()
        
        videoPath = getVideoPath(word)
        if videoPath:
            time.sleep(2)
            print(f"{Fore.CYAN}📁 Uploading {os.path.basename(videoPath)}...")
            handleFileUpload(driver, videoPath)
            
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ytcp-video-metadata-editor"))
            )
            print(f"{Fore.GREEN}✅ Upload started")
        
    except Exception as e:
        print(f"{Fore.RED}❌ Upload initiation error: {e}")

def uploadToYoutube(word, caption):
    try:
        title = f"{word.upper()}"
        description = caption
        tags = "GRE, IELTS, vocabulary, english, learning, education, words, study, exam prep, english vocabulary"
        
        chromePath = getChromePath()
        url = 'https://studio.youtube.com/channel/UCHvf5d1izlR4MR786HJzoew'
        userDataDir = pathStr(INS_CHROME_DATA_DIR)
        
        osName = "Windows" if os.name == "nt" else "Ubuntu"
        print(f"{Fore.MAGENTA}🚀 YouTube Upload - {word.upper()} ({osName})")
        print(f"{Fore.CYAN}{'='*50}")
        
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
        driver = webdriver.Chrome(options=chromeOptions)
        
        print(f"{Fore.GREEN}✅ Connected to Chrome ({osName})")
        
        clickCreateAndUpload(driver, word)
        
        print(f"{Fore.CYAN}📋 Configuring video...")
        fillTitleAndDescription(driver, title, description)
        selectFirstPlaylist(driver)
        setNotMadeForKids(driver)
        expandAdvancedOptions(driver)
        addTags(driver, tags)
        setCategoryToEntertainment(driver)
        
        print(f"{Fore.CYAN}🔄 Processing...")
        clickNextButton(driver)
        clickNextButton(driver)
        clickNextButton(driver)
        
        time.sleep(3)
        setPublicAndSave(driver)
        
        uploadSuccess = waitForUploadCompletion(driver)
        
        print(f"{Fore.MAGENTA}{'='*50}")
        if uploadSuccess:
            print(f"{Fore.GREEN}🎉 YouTube Upload Complete!")
        else:
            print(f"{Fore.RED}❌ Upload Failed")
        print(f"{Fore.YELLOW}🌐 Browser open for verification")
        print(f"{Fore.MAGENTA}{'='*50}")
        
        return uploadSuccess
        
    except Exception as e:
        print(f"{Fore.RED}❌ YouTube upload error: {e}")
        return False


def main():
    word = "Fallow"
    caption = "FALLOW means allowing land to remain uncultivated for a period to restore its fertility."
    
    result = uploadToYoutube(word, caption)
    print(f"{Fore.GREEN if result else Fore.RED}{'✅ Success' if result else '❌ Failed'}")

if __name__ == "__main__":
    main()
