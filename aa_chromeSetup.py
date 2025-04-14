#!/usr/bin/env python3
"""
Chrome Setup Script - Create a profile session for scraping

This script opens a Chrome browser with a specific profile directory,
allowing users to manually log in to websites and set up extensions.
The browser session will be saved for later use by scraping scripts.

Usage:
    python chrome_setup.py [URL]
"""

import os
import sys
import subprocess
import time
from config import (
    CHROME_DATA_DIR, DEBUGGING_PORT, CHROME_PATH as CONFIG_CHROME_PATH, 
    path_str, ensure_dirs_exist
)

def get_chrome_path():
    """Determine the Chrome executable path"""
    # Use Chrome path from config if available
    if CONFIG_CHROME_PATH:
        chrome_path = CONFIG_CHROME_PATH
        if not os.path.exists(chrome_path):
            print(f"Warning: Configured Chrome path {chrome_path} does not exist")
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
    ensure_dirs_exist()
    
    # Get Chrome path
    chrome_path = get_chrome_path()
    print(f"Chrome executable path: {chrome_path}")
    
    # Get user data directory path
    user_data_dir = path_str(CHROME_DATA_DIR)
    print(f"Chrome user data directory: {user_data_dir}")
    
    # Determine the URL to open
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = "https://www.google.com"
    
    print(f"Opening Chrome to URL: {url}")
    print("=" * 80)
    print("SETUP INSTRUCTIONS:")
    print("1. The Chrome browser will open with a clean profile")
    print("2. Log in to your Google account and any other required websites")
    print("3. Make sure you're logged in to https://www.playphrase.me/ if needed")
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
        print(f"Error: {e}")
    
    print("Setup complete. You can now run the scraping scripts.")

if __name__ == "__main__":
    main() 