from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
from tqdm import tqdm  # Import tqdm

filePath = "greWords.json"
with open(filePath, "r") as file:
    data = json.load(file)

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
# chrome_options.add_argument("--incognito")
def clearCookies():
    driver.delete_all_cookies()
    driver.execute_script("window.localStorage.clear();")
    driver.execute_script("window.sessionStorage.clear();")
    driver.execute_script("window.location.reload();")


try:
    for currentWord, wordData in data.items():
        print(data.keys().index(currentWord))
        if not wordData["searched"]:
            driver = webdriver.Chrome(options=chrome_options)
            driver.maximize_window()
            driver.get('https://www.google.com/')

            driver.get("https://www.playphrase.me/#/search?q=" + currentWord)
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'app')) and EC.presence_of_element_located((By.CLASS_NAME, 'video-player-container')))
            currentIndex = 1
            try:
                for _ in range(4):
                    element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'video-player-container')))
                    sleep(1)
                    videoData = element.find_element(By.TAG_NAME, "video")
                    videoURL = videoData.get_attribute("src")

                    subtitleData = element.find_elements(By.CLASS_NAME, "s-word")
                    subtitle = ' '.join([subtitle.text for subtitle in subtitleData])

                    videoInfoData = driver.find_elements(By.CLASS_NAME, "overlay-video-info")
                    for info in videoInfoData:
                        if info.text.strip() != "Download video":
                            videoInfo = info.text.strip()
                            break
                    else: videoInfo = "N/A"

                    data[currentWord]["clipData"][currentIndex] = {"videoURL": videoURL, "subtitle": subtitle, "videoInfo": videoInfo}
                    data[currentWord]["searched"] = True
                    currentIndex += 1

                    buttonsData = driver.find_elements(By.CLASS_NAME, "input-button")
                    for buttonData in buttonsData:
                        if buttonData.find_element(By.TAG_NAME, "i").text == "skip_next":
                            buttonData.click()
                            sleep(2)
                            break
                    else: break
            except Exception as e:
                data[currentWord]["searched"] = True
                print("Error waiting for page data to load:", e)
            finally: 
                driver.quit()
            # clearCookies()
                sleep(2)
                data[currentWord]["clipsFound"] = len(data[currentWord]["clipData"])
                with open(filePath, "w") as file: json.dump(data, file, indent=2)

except Exception as e: print("Error during processing:", e)
finally: driver.quit()
            