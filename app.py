import subprocess
from time import sleep
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import json, os

# Read the JSON file
with open('uploadData.json') as f:
    data = json.load(f)

chrome_driver_path = '/usr/lib/chromium-browser/chromedriver'
subprocess.Popen(['/usr/bin/google-chrome', '--remote-debugging-port=8989', '--user-data-dir=/home/midhdesk0/Desktop/GRE-Words/chromeData/'])
# subprocess.Popen(['C:/Program Files/Google/Chrome/Application/chrome.exe', '--remote-debugging-port=8989', '--user-data-dir=C:/chromeDriver/linkedInData/'])
sleep(2)
options = Options()
options.add_experimental_option("debuggerAddress", "localhost:8989")

# options.add_argument("--start-maximized")
options.add_argument(f"webdriver.chrome.driver={chrome_driver_path}")
options.add_argument("--disable-notifications")
driver = webdriver.Chrome(options=options)

driver.get("https://www.instagram.com/")
thisCaption = """No problem! Here's the information about the Mercedes CLR GTR:

The Mercedes CLR GTR is a remarkable racing car celebrated for its outstanding performance and sleek design. Powered by a potent 6.0-liter V12 engine, it delivers over 600 horsepower.

Acceleration from 0 to 100 km/h takes approximately 3.7 seconds, with a remarkable top speed surprising 320 km/h.🥇

Incorporating adventure aerodynamic features and cutting-edge stability technologies, the CLR GTR ensures exceptional stability and control, particularly during high-speed maneuvers. 💨

Originally priced at around $1.5 million, the Mercedes CLR GTR is considered one of the most exclusive and prestigious racing cars ever produced. 💰

Its limited production run of just five units adds to its rarity, making it highly sought after by racing enthusiasts and collectors worldwide. 🌎"""

if __name__ == "__main__":
    currentPage = 0
    sleep(2)
    createButton = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Create']")))
    createButton.click()
    sleep(2)
    postButton = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Post']")))
    postButton.click()
    sleep(2)
    selectButton = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='Select from computer']")))
    selectButton.click()
    # <button class=" _acan _acap _acas _aj1- _ap30" type="button"></button>
    os.system("xdotool key ctrl+l")
    sleep(1)

    firstVideo = data.get('unaddedVideos', [])[0] if 'unaddedVideos' in data else None
    print(0,0,100000,10000,1000,100,10,firstVideo)
    os.system(f"xdotool type '/home/midhdesk0/Desktop/GRE-Words/{firstVideo}' && xdotool key Return")

    try:
        selectButton = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, "//button[text()='OK']")))
        selectButton.click()
    except:
        print("IDK")

    # ratioButton = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "._acan._acao._acas._aj1-._ap30")))
    # ratioButton = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, '_acan') and contains(@class, '_acao') and contains(@class, '_acas') and contains(@class, '_aj1-') and contains(@class, '_ap30')]")))
    sleep(5)

    try:
        element = driver.find_element(By.CSS_SELECTOR, "._abfz._abg1")
        print("Element found.")
        element.click()
    except NoSuchElementException:
        print("Element not found.")
    # ratioButton.click()

    selectRatio = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='9:16']")))
    selectRatio.click()

    nextButton = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Next']")))
    nextButton.click()
    sleep(1)
    nextButton = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Next']")))
    nextButton.click()

    currentWord = firstVideo.split("/")[-1].replace(".mp4","")
    print(currentWord)
    # thisCaption = f"Current Word: {currentWord} \nFollow to learn New English Words everyday.\n\n#vocab #grevocabulary #grewords #grevocab #ielts #vocab #learning #english #word #wordofgod #wordgasm #wordoftheday #wordofday #meme"
    print(thisCaption)

    ratioButton = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".xw2csxc.x1odjw0f.x1n2onr6.x1hnll1o.xpqswwc.xl565be.x5dp1im.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.x1w2wdq1.xen30ot.x1swvt13.x1pi30zi.xh8yej3.x5n08af.notranslate")))
    ratioButton.send_keys(thisCaption)

    nextButton = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//div[text()='Share']")))
    nextButton.click()

    if firstVideo in data["unaddedVideos"]:
        data["unaddedVideos"].remove(firstVideo)
        data["addedVideos"].append(firstVideo)

    # Write the updated JSON data back to the file
    with open('uploadData.json', 'w') as file:
        json.dump(data, file, indent=4)
    driver.quit()