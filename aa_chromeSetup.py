import os
import sys
import subprocess
import time
from utils import error, warning
from config import (
    SCR_CHROME_DATA_DIR, INS_CHROME_DATA_DIR, DEBUGGING_PORT, CHROME_PATH as CONFIG_CHROME_PATH, 
    pathStr, ensureDirsExist
)

def getChromePath():
    """Determine the Chrome executable path"""
    if CONFIG_CHROME_PATH:
        chromePath = CONFIG_CHROME_PATH
        if not os.path.exists(chromePath):
            print(warning(f"⚠️  Configured Chrome path {chromePath} does not exist"))
        else:
            return chromePath

    if os.name == "nt":  # Windows
        chromePath = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        if not os.path.exists(chromePath):
            chromePath = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
    else:  # Linux/Mac
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
                    print("❌ Chrome executable not found. Please install Chrome or specify its path.")
                    print("💡 You can set the CHROME_PATH in the .env file.")
                    sys.exit(1)
    
    return chromePath

def main():
    ensureDirsExist()
    
    chromePath = getChromePath()
    print(f"🔍 Chrome executable: {chromePath}")
    
    print("\n📋 Select Chrome profile:")
    print("  1️⃣  Scraping Profile (SCR)")
    print("  2️⃣  Instagram Profile (INS)")
    print("  3️⃣  YouTube Profile (same as Instagram)")
    
    while True:
        profileChoice = input("\n🎯 Enter your choice (1, 2, or 3): ").strip()
        
        if profileChoice == "1":
            userDataDir = pathStr(SCR_CHROME_DATA_DIR)
            profileName = "Scraping"
            break
        elif profileChoice == "2":
            userDataDir = pathStr(INS_CHROME_DATA_DIR)
            profileName = "Instagram"
            break
        elif profileChoice == "3":
            userDataDir = pathStr(INS_CHROME_DATA_DIR)
            profileName = "YouTube (Instagram Profile)"
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")
    
    print(f"✅ Using {profileName} profile")
    print(f"📁 Data directory: {userDataDir}")
    
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        if profileChoice == "1":
            url = "https://www.playphrase.me/"
        elif profileChoice == "2":
            url = "https://www.instagram.com/"
        else:
            url = "https://studio.youtube.com/channel/UCHvf5d1izlR4MR786HJzoew"
    
    print(f"🌐 Opening: {url}")
    print("\n" + "="*60)
    print("🚀 SETUP INSTRUCTIONS")
    print("="*60)
    print(f"1️⃣  Chrome will open with the {profileName} profile")
    print("2️⃣  Log in to your Google account and required websites")
    if profileChoice == "1":
        print("3️⃣  Ensure you're logged in to playphrase.me")
    elif profileChoice == "2":
        print("3️⃣  Complete Instagram login and setup")
    elif profileChoice == "3":
        print("3️⃣  Verify YouTube Studio access and channel settings")
        print("4️⃣  Configure upload preferences")
    print("🔧 Configure extensions and persistent settings")
    print("⏰ Keep browser open during setup")
    print("💾 Session data will be automatically saved")
    print("="*60)
    
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
        print("🚀 Starting Chrome session...")
        chromeProcess = subprocess.Popen(chromeArgs)
        
        print("✨ Chrome is running. Complete setup, then close browser when done.")
        print("⚠️  Press Ctrl+C to force quit Chrome.")
        
        chromeProcess.wait()
        print("✅ Chrome session closed. Profile saved successfully!")
        print(f"💾 Session data stored in: {userDataDir}")
        
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user. Closing Chrome...")
        try:
            chromeProcess.terminate()
            chromeProcess.wait(timeout=5)
        except:
            print("🔄 Forcing Chrome to close...")
            chromeProcess.kill()
        print("✅ Chrome closed.")
    
    except Exception as e:
        print(error(f"❌ Error: {e}"))
    
    print("🎉 Setup complete. Ready to run scraping scripts!")

if __name__ == "__main__":
    main() 