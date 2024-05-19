
import os
import json
import subprocess

import subprocess

def concatVideos(videoList, outputPath):
    with open('videoList.txt', 'w') as file:
        for video in videoList:
            file.write(f"file '{video}'\n")
        # file.write(f"file 'videoResources/endVideo.mp4'\n")

    ffmpeg_command = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',  # Allow unsafe file names
        '-i', 'videoList.txt',
        '-c', 'copy',
        outputPath
    ]
    subprocess.run(ffmpeg_command)
    os.remove('videoList.txt')

with open("videoResources/greWords.json", "r") as allWords:
    allWordsData = json.load(allWords)

for currentWord, wordData in allWordsData.items():
    videosToMerge = []
    for i in range(1, wordData['clipsFound'] + 1):
        allVideoDir = f"mergedVideos/{currentWord}{i}.mp4"
        if os.path.exists(allVideoDir):
            videosToMerge.append(allVideoDir)

    if len(videosToMerge) >= 1:
        print(f"Merging videos for {currentWord.upper()}")
        outputPath = f'finalVideos/{currentWord.capitalize()}.mp4'
        concatVideos(videosToMerge, outputPath)
