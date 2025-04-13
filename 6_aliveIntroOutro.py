import os
import json
import sys
import subprocess
from config import (
    IMAGES_DIR, MERGED_VIDEOS_DIR, 
    path_str, ensure_dirs_exist
)

ensure_dirs_exist()

def create_video_from_image(imageLocation, outputLocation, duration, fadeIn=False, fadeOut=False):
    """
    Convert a static image to a video with specified duration
    
    Parameters:
    - imageLocation: path to the input image
    - outputLocation: path to save the output video
    - duration: duration of video in seconds
    - fadeIn: add fade-in effect if True
    - fadeOut: add fade-out effect if True
    """
    filter_complex = []
    
    if fadeIn and fadeOut:
        filter_complex = [
            'fade=t=in:st=0:d=1',
            'fade=t=out:st=' + str(duration-1) + ':d=1'
        ]
    elif fadeIn:
        filter_complex = ['fade=t=in:st=0:d=1']
    elif fadeOut:
        filter_complex = ['fade=t=out:st=' + str(duration-1) + ':d=1']
        
    filter_str = ','.join(filter_complex) if filter_complex else 'null'
    
    # Create video with standardized audio settings
    ffmpeg_command = [
        'ffmpeg',
        '-loop', '1',
        '-i', imageLocation,
        '-f', 'lavfi',
        '-i', 'anullsrc=r=44100:cl=stereo',
        '-t', str(duration),
        '-vf', filter_str,
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-b:a', '192k',         # Fixed audio bitrate
        '-ar', '44100',         # Fixed audio sample rate
        '-ac', '2',             # Fixed audio channels (stereo)
        '-shortest',
        '-tune', 'stillimage',
        '-pix_fmt', 'yuv420p',
        '-y', outputLocation
    ]
    
    try:
        subprocess.run(ffmpeg_command)
        print(f"Successfully created video: {os.path.basename(outputLocation)}")
        return True
    except Exception as e:
        print(f"Error running ffmpeg: {e}")
        return False

def process_intro_outro_videos():
    """
    Creates videos from intro and outro images
    """
    # Define paths with simple names
    intro_image = os.path.join(path_str(IMAGES_DIR), "intro.png")
    outro_image = os.path.join(path_str(IMAGES_DIR), "outro.png")
    
    intro_video = os.path.join(path_str(MERGED_VIDEOS_DIR), "intro.mp4")
    outro_video = os.path.join(path_str(MERGED_VIDEOS_DIR), "outro.mp4")
    
    if not os.path.exists(intro_image):
        print(f"Intro image not found: {intro_image}")
        return False
        
    if not os.path.exists(outro_image):
        print(f"Outro image not found: {outro_image}")
        return False
    
    print("Creating intro video (3 seconds)...")
    intro_success = create_video_from_image(intro_image, intro_video, 3, fadeIn=True, fadeOut=False)
    
    print("Creating outro video (5 seconds)...")
    outro_success = create_video_from_image(outro_image, outro_video, 5, fadeIn=False, fadeOut=True)
    
    if intro_success and outro_success:
        print("\nSuccessfully created intro and outro videos:")
        print(f"Intro: {intro_video}")
        print(f"Outro: {outro_video}")
        return True
    else:
        print("\nFailed to create some videos.")
        return False

if __name__ == "__main__":
    print("Creating intro and outro videos from images...")
    process_intro_outro_videos() 