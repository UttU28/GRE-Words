import os
import sys
import subprocess
import contextlib
from tqdm import tqdm
from utils import success, error, info, warning, highlight
from config import (
    MERGED_VIDEOS_DIR, FINAL_VIDEOS_DIR,
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

def concatVideos(videoList, outputPath):
    if not videoList:
        return False
        
    with open('videoList.txt', 'w') as file:
        for video in videoList:
            file.write(f"file '{video}'\n")

    ffmpegCommand = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',
        '-i', 'videoList.txt',
        '-filter_complex', 
        '[0:v]concat=n=' + str(len(videoList)) + ':v=1:a=1[outv][outa]',
        '-map', '[outv]', 
        '-map', '[outa]',
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-ar', '44100',
        '-y',
        outputPath
    ]
    
    try:
        with SuppressOutput():
            process = subprocess.run(ffmpegCommand, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            if process.returncode != 0:
                fallbackCommand = [
                    'ffmpeg',
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', 'videoList.txt',
                    '-c:v', 'libx264',
                    '-c:a', 'aac',
                    '-ar', '44100',
                    '-y',
                    outputPath
                ]
                subprocess.run(fallbackCommand, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
        if os.path.exists('videoList.txt'):
            os.remove('videoList.txt')
        return True
    except Exception as e:
        if os.path.exists('videoList.txt'):
            os.remove('videoList.txt')
        return False

def mergeWordVideos(word, includeIntroOutro=True):
    wordRow = db.getWord(word)
    
    if not wordRow:
        print(error(f"Word '{word}' not found in database"))
        return False
    
    wordId = wordRow['id']
    
    clips = db.getClipsForWord(wordId)
    
    if not clips:
        print(warning(f"No clip data found for '{word}'"))
        return False
    
    contentVideos = []
    
    introPath = os.path.join(pathStr(MERGED_VIDEOS_DIR), "intro.mp4")
    outroPath = os.path.join(pathStr(MERGED_VIDEOS_DIR), "outro.mp4")
    
    hasIntro = os.path.exists(introPath) and includeIntroOutro
    hasOutro = os.path.exists(outroPath) and includeIntroOutro
    
    progressBar = tqdm(total=4, desc=f"Creating final video for: {word.upper()}", unit="step")
    
    # Step 1: Find all clips
    for clip in clips:
        index = clip['clip_index']
        videoPath = os.path.join(pathStr(MERGED_VIDEOS_DIR), f"{word}{index}.mp4")
        if os.path.exists(videoPath):
            contentVideos.append(videoPath)
            
    progressBar.update(1)

    if len(contentVideos) >= 1:
        # Step 2: Merge content videos
        contentOnlyPath = os.path.join(pathStr(FINAL_VIDEOS_DIR), f"{word}_content_temp.mp4")
        contentResult = concatVideos(contentVideos, contentOnlyPath)
        
        if not contentResult:
            progressBar.close()
            print(error(f"Failed to merge content videos for {word}"))
            return False
            
        progressBar.update(1)
        
        finalOutputPath = os.path.join(pathStr(FINAL_VIDEOS_DIR), f"{word.capitalize()}.mp4")
        
        # If no intro/outro needed, just rename the content file
        if not hasIntro and not hasOutro:
            try:
                os.rename(contentOnlyPath, finalOutputPath)
                progressBar.update(2)
                progressBar.close()
                
                print(success(f"Final video created successfully: {word.capitalize()}.mp4"))
                return True
            except Exception as e:
                progressBar.close()
                print(error(f"Error renaming file: {e}"))
                return False
        
        # Step 3: Prepare for adding intro/outro
        progressBar.update(1)
        
        finalList = []
        if hasIntro:
            finalList.append(introPath)
        
        finalList.append(contentOnlyPath)
        
        if hasOutro:
            finalList.append(outroPath)
        
        # Step 4: Final merge with intro/outro
        finalResult = concatVideos(finalList, finalOutputPath)
        
        if os.path.exists(contentOnlyPath):
            os.remove(contentOnlyPath)
            
        progressBar.update(1)
        progressBar.close()
            
        if finalResult:
            print(success(f"Final video created successfully: {word.capitalize()}.mp4"))
            return True
        else:
            print(error(f"Failed to create final video for {word}"))
            return False
    else:
        progressBar.close()
        print(warning(f"No merged videos found for {word}"))
        return False

if __name__ == "__main__":
    includeIntroOutro = True
    
    if len(sys.argv) > 1:
        word = sys.argv[1].lower().strip()
        
        if len(sys.argv) > 2 and sys.argv[2] == "0":
            includeIntroOutro = False
        
        mergeWordVideos(word, includeIntroOutro)
    else:
        word = "nuance"
        if word:
            mergeWordVideos(word, includeIntroOutro)
        else:
            print(error("No word provided. Exiting."))

