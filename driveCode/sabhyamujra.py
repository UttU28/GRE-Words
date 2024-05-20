"""# **CLEAR EVERYTHING BOIIIIIIIIIIIIII**"""

import os, shutil
folders = ['finalVideos', 'images', 'mergedVideos']
for folder in folders:
    for filename in os.listdir(folder):
        print(filename)
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

"""# **DOWNLOADING VIDEOS TO THE DRIVE**"""

import os
import json
import requests

file_path = "videoResources/greWords.json"

with open(file_path, "r") as file:
    data = json.load(file)

outputDirectory = "downloadedVideos/"
os.makedirs(outputDirectory, exist_ok=True)

# Function to download videos for a specific batch
def download_batch(start_index, end_index):
    for currentWord, wordData in list(data.items())[start_index:end_index]:
        for clip_index, clip_info in wordData["clipData"].items():
            video_url = clip_info["videoURL"]
            video_info = clip_info["videoInfo"]

            # os.makedirs(os.path.join(outputDirectory, currentWord), exist_ok=True)

            file_name = f"{currentWord}_clip{clip_index}_{video_info.replace(' ', '_')}.mp4"
            file_path = os.path.join(outputDirectory, f"{currentWord}{clip_index}.mp4")

            response = requests.get(video_url, stream=True)
            with open(file_path, "wb") as video_file:
                for chunk in response.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        video_file.write(chunk)

            print(f"Downloaded video: {file_name}")

# Define batch size
batch_size = 10

# Calculate the number of batches
num_batches = (len(data) + batch_size - 1) // batch_size

try:
    batch_number = 1
    if 1 <= batch_number <= num_batches:
        start_index = (batch_number - 1) * batch_size
        end_index = min(batch_number * batch_size, len(data))
        download_batch(start_index, end_index)
    else:
        print("Invalid batch number.")
except ValueError:
    print("Invalid input. Please enter a number.")

"""# **MAKING IMAGES BOIIII**"""

import os
import json
import re
from PIL import Image, ImageFont, ImageDraw
import textwrap


with open("videoResources/greWords.json", "r") as allWords:
    allWordsData = json.load(allWords)


sampleText = ImageFont.truetype("fonts/edo.ttf", 40)
currentWordFont = ImageFont.truetype("fonts/Roboto-Black.ttf", 75)
currentDefFont = ImageFont.truetype("fonts/Roboto-Black.ttf", 50)
currentSubtitleFont = ImageFont.truetype("fonts/Roboto-Black.ttf", 50)
Font = ImageFont.truetype("fonts/Roboto-Black.ttf", 35)

def hex2rgb(rgbColor):
    return tuple(int(rgbColor[i:i+2], 16) for i in (1, 3, 5))

def getWrappedText(text: str, font: ImageFont.ImageFont, line_length: int):
    lines = ['']
    for word in text.split():
        line = f'{lines[-1]} {word}'.strip()
        if font.getlength(line) <= line_length:
            lines[-1] = line
        else:
            lines.append(word)
    return '\n'.join(lines)

def imageTextGenerator(draw, text, currentSubtitleFont, paddingTop):
    maxFontWidth = 1080 - 100
    maxFontHeight = 1920 - 100
    finalMultilineText = ""
    finalTitleFont = None
    multilineText = getWrappedText(text, currentSubtitleFont, maxFontWidth)
    _, _, w, h = draw.multiline_textbbox((0, 0), multilineText, font=currentSubtitleFont)
    if not (w > maxFontWidth or h > maxFontHeight):
        finalMultilineText = multilineText
        finalTitleFont = currentSubtitleFont

    x = 50 + (1080 - 100) / 2
    y = paddingTop
    return finalMultilineText, finalTitleFont, x, y

def generateImage(currentWord, currentDef, currentSubtitle, currentMovie, index):
    originalImage = "videoResources/woKyaBolRahi.png"
    original_image = Image.open(originalImage)
    img = original_image.copy()

    draw = ImageDraw.Draw(img)

    draw.text((50, 275), "TODAY'S WORD", font=sampleText, fill='#f88f55')
    multilineText, font, positionX, positionY = imageTextGenerator(draw, currentWord.upper(), currentWordFont, paddingTop=310)
    draw.multiline_text(xy=(positionX, positionY), text=multilineText, font=font, align="center", fill="#77e03a", anchor="ma")

    draw.text((50, 410), "DEFINITION", font=sampleText, fill='#f88f55')
    wrappedText = textwrap.fill(currentDef, width=45)  # Adjust the width as needed
    text_position = (50, 445)
    multilineText, font, positionX, positionY = imageTextGenerator(draw, currentDef, currentDefFont, paddingTop=450)
    draw.multiline_text(xy=(positionX, positionY), text=multilineText, font=font, align="left", fill="#77e03a", anchor="ma")
    # bbox = draw.multiline_text(xy=(positionX, positionY), text=multilineText, font=font, align="left", fill="#77e03a", anchor="ma")

    bbox = draw.textbbox(text_position, wrappedText, font=currentDefFont)
    videoStartHeight = abs(bbox[1] - bbox[3]) + 500
    draw.text((50, videoStartHeight), f"SOURCE: {currentMovie}", font=sampleText, fill='#f88f55')

    videoStartHeight += 50
    videoEndHeight = videoStartHeight + 800
    multilineText, font, positionX, positionY = imageTextGenerator(draw, currentSubtitle, currentSubtitleFont, paddingTop=videoEndHeight)
    draw.multiline_text(xy=(positionX, positionY), text=multilineText, font=font, align="center", fill="#e5efac", anchor="ma")

    # img.show()
    # img.save("image.png", "PNG")
    img.save(f"images/{currentWord}{index}.png", "PNG")

    return videoStartHeight


def updateJsonFile(currentKey, currentIndex, videoStartHeight):
    with open("videoResources/greWords.json", 'r') as file:
        data = json.load(file)

    if currentKey in data:
        data[currentKey]["clipData"][currentIndex]["videoStartHeight"] = videoStartHeight
        print(f"Updated '{currentKey}' to '{videoStartHeight}'")
    else:
        print(f"Key '{currentKey}' not found in the JSON file")

    with open("videoResources/greWords.json", 'w') as file:
        json.dump(data, file, indent=2)

def upperText(inputString, thisWord):
    pattern = re.compile(r'\b' + re.escape(thisWord) + r'\b', re.IGNORECASE)
    return pattern.sub(thisWord.upper(), inputString)

def makeImagesInBatch(start_index, end_index):
    for currentWord, wordData in list(allWordsData.items())[start_index:end_index]:
    # for currentWord, wordData in allWordsData.items():
        if not wordData["wordUsed"]:
            currentDef = wordData['meaning']
            # print(currentWord, currentDef)
            for index, videoData in wordData["clipData"].items():
                currentSubtitle = upperText(videoData["subtitle"], currentWord)
                currentMovie = videoData["videoInfo"]
                # print(currentSubtitle)
                videoStartHeight = generateImage(currentWord, currentDef, currentSubtitle, currentMovie, index)
                updateJsonFile(currentWord, str(index), videoStartHeight)
        #         break
        # break

batch_size = 10
num_batches = (len(allWordsData) + batch_size - 1) // batch_size

try:
    batch_number = 1
    if 1 <= batch_number <= num_batches:
        start_index = (batch_number - 1) * batch_size
        end_index = min(batch_number * batch_size, len(allWordsData))
        makeImagesInBatch(start_index, end_index)
    else:
        print("Invalid batch number.")
except ValueError:
    print("Invalid input. Please enter a number.")

"""# **ADDING TEXT TO VIDEOS INDIVIDUALLY**"""

import os
import json
import re
import subprocess

def mergingVideoAndImage(imageLocation, videoLocation, outputLocation, videoStartHeight):
    ffmpeg_command = [
        'ffmpeg',
        '-loop', '1', '-i', imageLocation,
        '-i', videoLocation,
        '-filter_complex', f'[1]scale=1000:750[inner];[0][inner]overlay=50:{videoStartHeight+25}:shortest=1[out]',
        '-map', '[out]', '-map', '1:a',
        '-c:a', 'copy',
        '-y', outputLocation
    ]
    subprocess.run(ffmpeg_command)

with open("videoResources/greWords.json", "r") as allWords:
    allWordsData = json.load(allWords)

def addVideoToImage(start_index, end_index):
    for currentWord, wordData in list(allWordsData.items())[start_index:end_index]:
        currentDef = wordData['meaning']
        # print(currentWord, currentDef)
        for index, videoData in wordData["clipData"].items():
            imageLocation = f"images/{currentWord}{index}.png"
            videoLocation = f"downloadedVideos/{currentWord}{index}.mp4"
            outputLocation = f"mergedVideos/{currentWord}{index}.mp4"
            videoStartHeight = videoData["videoStartHeight"]
            mergingVideoAndImage(imageLocation, videoLocation, outputLocation, videoStartHeight)
            print(f"Done with {currentWord}, index = {index}")
        #     break
        # break

batch_size = 10
num_batches = (len(allWordsData) + batch_size - 1) // batch_size

try:
    batch_number = 1
    if 1 <= batch_number <= num_batches:
        start_index = (batch_number - 1) * batch_size
        end_index = min(batch_number * batch_size, len(allWordsData))
        addVideoToImage(start_index, end_index)
    else:
        print("Invalid batch number.")
except ValueError:
    print("Invalid input. Please enter a number.")

"""# **MERGING VIDEOS OF EACH WORD**"""

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

"""# **KACHRA NAHI HAI MEHNAT HAI YE**"""