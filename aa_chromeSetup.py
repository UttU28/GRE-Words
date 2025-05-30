import os
import sys
import subprocess
import time
from utils import error, warning
from config import (
    SCR_CHROME_DATA_DIR, INS_CHROME_DATA_DIR, DEBUGGING_PORT, CHROME_PATH as CONFIG_CHROME_PATH, 
    pathStr, ensureDirsExist
)

def get_chrome_path():
    """Determine the Chrome executable path"""
    # Use Chrome path from config if available
    if CONFIG_CHROME_PATH:
        chrome_path = CONFIG_CHROME_PATH
        if not os.path.exists(chrome_path):
            print(warning(f"Warning: Configured Chrome path {chrome_path} does not exist"))
        else:
            return chrome_path

    # Determine Chrome path based on OS
    if os.name == "nt":  # Windows
        chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        if not os.path.exists(chrome_path):
            chrome_path = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
    else:  # Linux/Mac
        # Check common Ubuntu locations
        chrome_path = "/usr/bin/google-chrome"
        if not os.path.exists(chrome_path):
            chrome_path = "/usr/bin/google-chrome-stable"
        if not os.path.exists(chrome_path):
            chrome_path = "/snap/bin/chromium"
        if not os.path.exists(chrome_path):
            # Try to find Chrome using which command
            try:
                chrome_path = subprocess.check_output(["which", "google-chrome"], text=True).strip()
            except subprocess.CalledProcessError:
                try:
                    chrome_path = subprocess.check_output(["which", "chrome"], text=True).strip()
                except subprocess.CalledProcessError:
                    print("Chrome executable not found. Please install Chrome or specify its path.")
                    print("You can set the CHROME_PATH in the .env file.")
                    sys.exit(1)
    
    return chrome_path

def main():
    # Ensure necessary directories exist
    ensureDirsExist()
    
    # Get Chrome path
    chrome_path = get_chrome_path()
    print(f"Chrome executable path: {chrome_path}")
    
    # Prompt user to select which profile to use
    print("Select which Chrome profile to use:")
    print("1. Scraping Profile (SCR)")
    print("2. Instagram Profile (INS)")
    print("3. YouTube Profile (same as Instagram)")
    
    while True:
        profile_choice = input("Enter your choice (1, 2, or 3): ").strip()
        
        if profile_choice == "1":
            user_data_dir = pathStr(SCR_CHROME_DATA_DIR)
            profile_name = "Scraping"
            break
        elif profile_choice == "2":
            user_data_dir = pathStr(INS_CHROME_DATA_DIR)
            profile_name = "Instagram"
            break
        elif profile_choice == "3":
            user_data_dir = pathStr(INS_CHROME_DATA_DIR)  # Use same profile as Instagram
            profile_name = "YouTube (Instagram Profile)"
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")
    
    print(f"Using {profile_name} profile.")
    print(f"Chrome user data directory: {user_data_dir}")
    
    # Determine the URL to open
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        # Set default URL based on profile choice
        if profile_choice == "1":
            url = "https://www.playphrase.me/"
        elif profile_choice == "2":
            url = "https://www.instagram.com/"
        else:  # profile_choice == "3"
            url = "https://studio.youtube.com/channel/UCHvf5d1izlR4MR786HJzoew"
    
    print(f"Opening Chrome to URL: {url}")
    print("=" * 80)
    print("SETUP INSTRUCTIONS:")
    print(f"1. The Chrome browser will open with the {profile_name} profile")
    print("2. Log in to your Google account and any other required websites")
    if profile_choice == "1":
        print("3. Make sure you're logged in to https://www.playphrase.me/ if needed")
    elif profile_choice == "2":
        print("3. Make sure you're logged in to Instagram and any other required sites")
    elif profile_choice == "3":
        print("3. Make sure you're logged in to YouTube Studio and verify channel access")
        print("4. Set up any YouTube upload preferences or settings")
    print("4. Configure any extensions or settings you want to persist")
    print("5. Keep the browser open as long as needed to complete setup")
    print("6. When done, you can close the browser manually")
    print("7. Your session data will be saved in the Chrome data directory")
    print("=" * 80)
    
    # Start Chrome process with debugging port
    chrome_args = [
        chrome_path,
        f"--remote-debugging-port={DEBUGGING_PORT}",
        f"--user-data-dir={user_data_dir}",
        "--disable-notifications",
        "--no-first-run",
        "--no-default-browser-check",
        "--disable-blink-features=AutomationControlled",
        url
    ]
    
    # Run Chrome and wait for user to manually close it
    try:
        print("Starting Chrome session...")
        chrome_process = subprocess.Popen(chrome_args)
        
        print("Chrome is running. Complete your login and setup, then close the browser when done.")
        print("Press Ctrl+C in this terminal to force quit Chrome.")
        
        # Wait for the process to complete
        chrome_process.wait()
        print("Chrome session closed. Your profile has been saved.")
        print(f"Session data is stored in: {user_data_dir}")
        
    except KeyboardInterrupt:
        print("\nInterrupted by user. Closing Chrome...")
        try:
            chrome_process.terminate()
            chrome_process.wait(timeout=5)
        except:
            print("Forcing Chrome to close...")
            chrome_process.kill()
        print("Chrome closed.")
    
    except Exception as e:
        print(error(f"Error: {e}"))
    
    print("Setup complete. You can now run the scraping scripts.")

if __name__ == "__main__":
    main() 