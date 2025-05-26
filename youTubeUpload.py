# Complete Python script to upload a video to YouTube using YouTube Data API v3
# using OAuth 2.0 Installed App Flow with a service client secret JSON file

import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

# Import common utilities
from utils import success, error, info, warning, highlight
from config import FINAL_VIDEOS_DIR, pathStr, ensureDirsExist

# Constants
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS_FILE = "client_secret.json"  # Replace with your file path
TOKEN_FILE = "token.pickle"

def get_authenticated_service():
    """Get authenticated YouTube service"""
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=8080, open_browser=True)
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    return build("youtube", "v3", credentials=creds)

def generate_tags(word, caption):
    """Generate relevant tags for the GRE word video"""
    # Base tags for GRE content
    base_tags = [
        "GRE", "GREprep", "vocabulary", "learnenglish", "wordoftheday",
        "englishvocabulary", "testprep", "education", "learning",
        "englishwords", "studyenglish", "vocabularybuilding"
    ]
    
    # Add the word itself
    word_tags = [word.lower(), word.upper()]
    
    # Add content-specific tags
    content_tags = [
        "grewords", "vocabularytest", "englishlearning", "wordmeaning",
        "definition", "pronunciation", "usage", "example", "sentence",
        "gradschool", "university", "academic", "standardizedtest"
    ]
    
    # Combine all tags and remove duplicates
    all_tags = list(set(base_tags + word_tags + content_tags))
    
    # YouTube allows max 500 characters for tags, so limit the number
    return all_tags[:15]  # Limit to 15 tags to stay within character limit

def upload_video(youtube, video_file, word, caption):
    """Upload video to YouTube with GRE word content"""
    
    # Generate tags based on word and content
    tags = generate_tags(word, caption)
    
    # Create video metadata
    body = {
        "snippet": {
            "title": word.upper(),  # Just the word name as title
            "description": f"{word.upper()}\n\n{caption}\n\n#GREprep #vocabulary #learnenglish #wordoftheday",
            "tags": tags,
            "categoryId": "27",  # Education category
            "defaultLanguage": "en",
            "defaultAudioLanguage": "en"
        },
        "status": {
            "privacyStatus": "private",  # Keep private as requested
            "selfDeclaredMadeForKids": False,  # Not for kids
            "embeddable": True,
            "publicStatsViewable": True
        }
    }

    print(info(f"Uploading video for word: {word.upper()}"))
    print(info(f"Title: {word.upper()}"))
    print(info(f"Tags: {', '.join(tags[:10])}..."))  # Show first 10 tags
    
    # Create media upload object
    media = MediaFileUpload(video_file, mimetype="video/*", resumable=True)

    # Create upload request
    request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media
    )

    # Execute upload with progress tracking
    response = None
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                progress = int(status.progress() * 100)
                print(info(f"Upload progress: {progress}%"))
        except Exception as e:
            print(error(f"Upload error: {e}"))
            return False

    if response:
        video_id = response['id']
        print(success("Upload Complete!"))
        print(success(f"Video ID: {video_id}"))
        print(success(f"Watch at: https://www.youtube.com/watch?v={video_id}"))
        return True
    else:
        print(error("Upload failed - no response received"))
        return False

def upload_to_youtube(word, caption, video_path=None):
    """
    Upload a video to YouTube using API
    
    Args:
        word (str): The GRE word being processed
        caption (str): The caption/description to use for the YouTube video
        video_path (str, optional): The path to the video file. If None, will be determined from the word.
    
    Returns:
        bool: Whether the upload was successful
    """
    
    # Determine video path if not provided
    if video_path is None:
        ensureDirsExist()
        videoDirPath = pathStr(FINAL_VIDEOS_DIR)
        capitalizedWord = word[0].upper() + word[1:]
        video_path = os.path.join(videoDirPath, capitalizedWord + ".mp4")
    
    print(highlight(f"\n=== YouTube API Upload Started for {word.upper()} ==="))
    
    # Check if video file exists
    if not os.path.exists(video_path):
        print(error(f"Video file {video_path} not found"))
        return False
    
    # Check if client secrets file exists
    if not os.path.exists(CLIENT_SECRETS_FILE):
        print(error(f"Client secrets file {CLIENT_SECRETS_FILE} not found"))
        print(warning("Please download your OAuth 2.0 credentials from Google Cloud Console"))
        print(info("1. Go to https://console.cloud.google.com/"))
        print(info("2. Enable YouTube Data API v3"))
        print(info("3. Create OAuth 2.0 credentials"))
        print(info("4. Download and save as 'client_secret.json'"))
        return False
    
    try:
        # Get authenticated YouTube service
        print(info("Authenticating with YouTube API..."))
        youtube = get_authenticated_service()
        print(success("Authentication successful!"))
        
        # Upload the video
        result = upload_video(youtube, video_path, word, caption)
        
        if result:
            print(success(f"YouTube upload completed successfully for {word.upper()}!"))
            return True
        else:
            print(error(f"YouTube upload failed for {word.upper()}"))
            return False
            
    except Exception as e:
        print(error(f"Error during YouTube upload: {e}"))
        return False

if __name__ == "__main__":
    # Test the function
    test_word = "Balk"
    test_caption = "To hesitate or refuse to proceed. When faced with the difficult decision, she began to balk at the idea of moving to a new city."
    upload_to_youtube(test_word, test_caption)
