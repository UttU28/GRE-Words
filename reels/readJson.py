import os
import json
from makeImage import generateImage
import re

with open("greWords.json", "r") as allWords:
    allWordsData = json.load(allWords)

def upperText(inputString, thisWord):
    pattern = re.compile(r'\b' + re.escape(thisWord) + r'\b', re.IGNORECASE)
    return pattern.sub(thisWord.upper(), inputString)

def download_batch(start_index, end_index):
    for currentWord, wordData in list(allWordsData.items())[start_index:end_index]:
    # for currentWord, wordData in allWordsData.items():
        if not wordData["wordUsed"]:
            currentDef = wordData['meaning']
            # print(currentWord, currentDef)
            for index, videoData in wordData["clipData"].items():
                currentSubtitle = upperText(videoData["subtitle"], currentWord)
                # print(currentSubtitle)
                generateImage(currentWord, currentDef, currentSubtitle, index)
                # videoLocation = f"./{currentWord}/{index}.mp4"
                # print(index, videoData['videoInfo'], videoLocation)

batch_size = 10
num_batches = (len(allWordsData) + batch_size - 1) // batch_size

try:
    batch_number = 1
    if 1 <= batch_number <= num_batches:
        start_index = (batch_number - 1) * batch_size
        end_index = min(batch_number * batch_size, len(allWordsData))
        download_batch(start_index, end_index)
    else:
        print("Invalid batch number.")
except ValueError:
    print("Invalid input. Please enter a number.")