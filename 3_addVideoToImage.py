import os
import sys
import subprocess
import contextlib
from tqdm import tqdm
from utils import success, error, info, warning, highlight
from config import (
    IMAGES_DIR, DOWNLOADED_VIDEOS_DIR, MERGED_VIDEOS_DIR,
    pathStr, ensureDirsExist
)
from db_controller import db

# Ensure necessary directories exist
ensureDirsExist()

class SuppressOutput:
    def __init__(self):
        self.null_fds = [os.open(os.devnull, os.O_RDWR) for _ in range(2)]
        self.save_fds = [os.dup(1), os.dup(2)]

    def __enter__(self):
        os.dup2(self.null_fds[0], 1)
        os.dup2(self.null_fds[1], 2)
        return self

    def __exit__(self, *_):
        os.dup2(self.save_fds[0], 1)
        os.dup2(self.save_fds[1], 2)
        for fd in self.null_fds + self.save_fds:
            os.close(fd)

def mergeVideoAndImage(imageLocation, videoLocation, outputLocation, videoStartHeight):
    fixedHeight = 500
    
    ffmpegCommand = [
        'ffmpeg',
        '-loop', '1', '-i', imageLocation,
        '-i', videoLocation,
        '-filter_complex', f'[1]scale=-1:{fixedHeight}[scaled];[scaled]setpts=PTS-STARTPTS[inner];[0][inner]overlay=(W-w)/2:{videoStartHeight+60}:shortest=1[out]',
        '-map', '[out]', '-map', '1:a',
        '-c:a', 'copy',
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        '-pix_fmt', 'yuv420p',
        '-y', outputLocation
    ]
    
    try:
        with SuppressOutput():
            subprocess.run(ffmpegCommand, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        return False

def processWord(word):
    # Get word data from database
    wordRow = db.getWord(word)
    
    if not wordRow:
        print(error(f"Word '{word}' not found in database"))
        return False
        
    wordId = wordRow['id']
    
    # Get all clips for this word
    clips = db.getClipsForWord(wordId)
    
    if not clips:
        print(warning(f"No clip data found for '{word}'"))
        return False
    
    clipsProcessed = 0
    
    progressBar = tqdm(clips, desc=f"Adding videos to images for: {word.upper()}", unit="video")
    
    for clip in progressBar:
        index = clip['clip_index']
        imageLocation = os.path.join(pathStr(IMAGES_DIR), f"{word}{index}.png")
        videoLocation = os.path.join(pathStr(DOWNLOADED_VIDEOS_DIR), f"{word}{index}.mp4")
        outputLocation = os.path.join(pathStr(MERGED_VIDEOS_DIR), f"{word}{index}.mp4")
        
        if not os.path.exists(imageLocation) or not os.path.exists(videoLocation):
            continue
        
        # Get videoStartHeight from database or use a default value
        videoStartHeight = 300  # Default value
        if 'video_start_height' in clip.keys() and clip['video_start_height'] is not None:
            videoStartHeight = clip['video_start_height']
        
        operationResult = mergeVideoAndImage(imageLocation, videoLocation, outputLocation, videoStartHeight)
        if operationResult:
            clipsProcessed += 1
    
    print(success(f"Total videos processed successfully: {clipsProcessed}"))
    
    return clipsProcessed > 0

if __name__ == "__main__":
    if len(sys.argv) > 1:
        word = sys.argv[1].lower().strip()
        processWord(word)
    else:
        # word = input("Enter the word to process videos for: ").lower().strip()
        word = "nuance"
        if word:
            processWord(word)
        else:
            print(error("No word provided. Exiting."))