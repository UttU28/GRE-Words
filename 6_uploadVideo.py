#!/usr/bin/env python3
import os
import sys
import subprocess
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from colorama import init, Fore, Style
from config import (
    INS_CHROME_DATA_DIR, DEBUGGING_PORT, CHROME_PATH as CONFIG_CHROME_PATH,
    FINAL_VIDEOS_DIR, pathStr, ensureDirsExist
)

init(autoreset=True)

# Path to the specific chromedriver
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
                    print(f"{Fore.RED}Chrome executable not found. Please install Chrome.")
                    sys.exit(1)
    
    return chromePath

def automateInstagramActions(debuggingPort, videoPath=None, caption="Instagram said 'post daily' — so here's me being obedient."):
    try:
        chromeOptions = Options()
        chromeOptions.add_experimental_option("debuggerAddress", f"localhost:{debuggingPort}")
        
        # Use the specific chromedriver
        service = Service(executable_path=CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=chromeOptions)
        
        print(f"{Fore.CYAN}Connected to Chrome. Starting automation...")
        
        createButton = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Create')]"))
        )
        createButton.click()
        
        if videoPath:
            if os.name == "nt":
                import pyautogui
                selectButton = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Select from computer')]"))
                )
                selectButton.click()
                
                time.sleep(2)
                pyautogui.write(videoPath, interval=0.05)
                time.sleep(1)
                pyautogui.press('enter')
                print(f"{Fore.GREEN}Selected video: {os.path.basename(videoPath)}")
            else:
                time.sleep(2)
                try:
                    uploadInput = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
                    )
                    uploadInput.send_keys(videoPath)
                    print(f"{Fore.GREEN}Selected video (Ubuntu method): {os.path.basename(videoPath)}")
                except Exception as e:
                    print(f"{Fore.RED}Could not find file input to upload video: {e}")
                    raise

            time.sleep(5)
            
            try:
                try:
                    cropButtonContainer = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[@class='_abfz _abg1' and @role='button']"))
                    )
                    cropButtonContainer.click()
                except Exception:
                    try:
                        cropButton = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, "//button[.//svg[@aria-label='Select crop']]"))
                        )
                        cropButton.click()
                    except Exception:
                        try:
                            cropSvg = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, "//svg[@aria-label='Select crop']"))
                            )
                            cropSvg.click()
                        except Exception:
                            raise Exception("Could not find crop button")
                
                time.sleep(2)
                try:
                    originalOption = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//span[text()='Original']"))
                    )
                    originalOption.click()
                except Exception:
                    try:
                        originalOption = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Original')]"))
                        )
                        originalOption.click()
                    except Exception:
                        raise Exception("Could not select Original format")
                
                time.sleep(2)
                
                try:
                    nextButton = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and text()='Next']"))
                    )
                    nextButton.click()
                except Exception:
                    try:
                        nextButton = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//*[text()='Next']"))
                        )
                        nextButton.click()
                    except Exception:
                        raise Exception("Could not click first Next button")
                
                time.sleep(3)
                
                try:
                    nextButton2 = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and text()='Next']"))
                    )
                    nextButton2.click()
                except Exception:
                    try:
                        nextButton2 = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//*[text()='Next']"))
                        )
                        nextButton2.click()
                    except Exception:
                        raise Exception("Could not click second Next button")
                
                time.sleep(3)
                
                try:
                    captionField = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[@aria-label='Write a caption...']"))
                    )
                    captionField.click()
                    time.sleep(1)
                    captionField.send_keys(caption)
                except Exception:
                    try:
                        captionField = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//div[@role='textbox']"))
                        )
                        captionField.click()
                        time.sleep(1)
                        captionField.send_keys(caption)
                    except Exception:
                        try:
                            captionField = driver.find_element(By.XPATH, "//div[@contenteditable='true']")
                            driver.execute_script("arguments[0].innerText = arguments[1]", captionField, caption)
                        except Exception:
                            raise Exception("Could not enter caption")
                
                print(f"{Fore.GREEN}Added caption")
                
                try:
                    accessibilityButton = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//span[text()='Accessibility']"))
                    )
                    accessibilityButton.click()
                except Exception:
                    try:
                        accessibilityDiv = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//div[.//span[contains(text(), 'Accessibility')]]"))
                        )
                        accessibilityDiv.click()
                    except Exception:
                        raise Exception("Could not click Accessibility button")
                
                time.sleep(2)
                
                try:
                    captionsToggle = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//input[@role='switch']"))
                    )
                    if captionsToggle.get_attribute("aria-checked") == "false":
                        captionsToggle.click()
                except Exception:
                    try:
                        captionsSection = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, "//span[contains(text(), 'Auto-generated captions')]"))
                        )
                        captionsToggle = captionsSection.find_element(By.XPATH, "./following::input[@type='checkbox']")
                        if captionsToggle.get_attribute("aria-checked") == "false":
                            captionsToggle.click()
                    except Exception:
                        print(f"{Fore.YELLOW}Could not enable auto-generated captions")
                
                print(f"{Fore.GREEN}Enabled auto-generated captions")
                
                # Click the share/submit button to post the content
                time.sleep(2)
                try:
                    shareButton = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and text()='Share']"))
                    )
                    shareButton.click()
                    print(f"{Fore.GREEN}Clicked Share button to post content")
                    
                    # Wait for post completion confirmation message (up to 1 minute)
                    try:
                        success_message = WebDriverWait(driver, 60).until(
                            EC.presence_of_element_located((By.XPATH, "//h3[contains(text(), 'Your reel has been shared')]"))
                        )
                        print(f"{Fore.GREEN}Post has been shared successfully - confirmation message detected")
                    except Exception as e:
                        print(f"{Fore.YELLOW}Warning: Could not detect share confirmation message: {e}")
                        # Continue anyway as the post might still have been successful
                except Exception:
                    try:
                        shareButton = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, "//*[text()='Share']"))
                        )
                        shareButton.click()
                        print(f"{Fore.GREEN}Clicked Share button to post content")
                        
                        # Wait for post completion confirmation message (up to 1 minute)
                        try:
                            success_message = WebDriverWait(driver, 60).until(
                                EC.presence_of_element_located((By.XPATH, "//h3[contains(text(), 'Your reel has been shared')]"))
                            )
                            print(f"{Fore.GREEN}Post has been shared successfully - confirmation message detected")
                        except Exception as e:
                            print(f"{Fore.YELLOW}Warning: Could not detect share confirmation message: {e}")
                            # Continue anyway as the post might still have been successful
                    except Exception as e:
                        print(f"{Fore.RED}Could not click Share button: {e}")
                
            except Exception as e:
                print(f"{Fore.RED}Error: {e}")
        
        print(f"{Fore.GREEN}Automation completed")
        return True
        
    except Exception as e:
        print(f"{Fore.RED}Error: {e}")
        return False

def main(word, caption):
    ensureDirsExist()
    
    chromePath = getChromePath()
    userDataDir = pathStr(INS_CHROME_DATA_DIR)
    
    videoDirPath = pathStr(FINAL_VIDEOS_DIR)
    capitalizedWord = word[0].upper() + word[1:]
    videoPath = os.path.join(videoDirPath, capitalizedWord + ".mp4")
    
    if not os.path.exists(videoPath):
        print(f"{Fore.RED}Error: Video file {videoPath} not found")
        return
    
    url = 'https://www.instagram.com/'
    
    print(f"{Fore.CYAN}Starting upload process for {Fore.YELLOW}{capitalizedWord}{Fore.CYAN}...")
    
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
    
    try:
        chromeProcess = subprocess.Popen(chromeArgs)
        time.sleep(5)
        
        automateInstagramActions(DEBUGGING_PORT, videoPath, caption)
        time.sleep(5)
        
        print(f"{Fore.CYAN}Complete the process in the browser. Press Ctrl+C to close Chrome.")
        
        # chromeProcess.wait()
        print(f"\n{Fore.YELLOW}Closing Chrome...")
        try:
            chromeProcess.terminate()
            chromeProcess.wait(timeout=5)
        except:
            chromeProcess.kill()        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Closing Chrome...")
        try:
            chromeProcess.terminate()
            chromeProcess.wait(timeout=5)
        except:
            chromeProcess.kill()
    
    except Exception as e:
        print(f"{Fore.RED}Error: {e}")
    
    print(f"{Fore.GREEN}Upload process completed")

if __name__ == "__main__":
    word = "nuance"
    caption = "Instagram said \"post daily\" — so here's me being obedient."
    main(word, caption) 
    