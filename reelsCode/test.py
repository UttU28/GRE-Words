
import os
import json
import subprocess

def concatVideos(videoList, outputPath):
    with open('videoList.txt', 'w') as file:
        for video in videoList:
            file.write(f"file '{video}'\n")
            file.write(f"file fillerVideo.mp4\n")
        file.write(f"file endVideo.mp4\n")
        # file.write(f"file 'videoResources/endVideo.mp4'\n")

    ffmpeg_command = [
        'ffmpeg', 
        '-f', 'concat', 
        '-i', 'videoList.txt',
        '-vf', 'fps=30,scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2', 
        '-b:v', '2M', 
        '-c:a', 'copy', 
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

