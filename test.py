import subprocess
from time import sleep
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
# import pyautogui as py
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException


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

if __name__ == "__main__":
    currentPage = 0
    sleep(2)
    createButton = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//span[text()='Create']"))
    )
    createButton.click()
    sleep(2)
    postButton = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//span[text()='Post']"))
    )
    postButton.click()
    sleep(2)
    selectButton = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[text()='Select from computer']"))
    )
    selectButton.click()
    # <button class=" _acan _acap _acas _aj1- _ap30" type="button"></button>


# driver.quit()