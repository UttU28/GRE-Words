import os
import json
import re
from PIL import Image, ImageFont, ImageDraw
import textwrap


with open("greWords.json", "r") as allWords:
    allWordsData = json.load(allWords)


sampleText = ImageFont.truetype("edo.ttf", 40)
currentWordFont = ImageFont.truetype("Roboto-Black.ttf", 75)
currentDefFont = ImageFont.truetype("Roboto-Black.ttf", 50)
currentSubtitleFont = ImageFont.truetype("Roboto-Black.ttf", 50)
Font = ImageFont.truetype("Roboto-Black.ttf", 35)

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

def generateImage(currentWord, currentDef, currentSubtitle, index):
    originalImage = "woKyaBolRahi.png"
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
    draw.text((50, videoStartHeight), "VIDEO", font=sampleText, fill='#f88f55')

    videoStartHeight += 50
    videoEndHeight = videoStartHeight + 800
    multilineText, font, positionX, positionY = imageTextGenerator(draw, currentSubtitle, currentSubtitleFont, paddingTop=videoEndHeight)
    draw.multiline_text(xy=(positionX, positionY), text=multilineText, font=font, align="center", fill="#e5efac", anchor="ma")

    # img.show()
    # img.save("image.png", "PNG")
    img.save(f"./images/{currentWord}{index}.png", "PNG")

    return videoStartHeight


def updateJsonFile(currentKey, currentIndex, videoStartHeight):
    with open("greWords.json", 'r') as file:
        data = json.load(file)

    if currentKey in data:
        data[currentKey]["clipData"][currentIndex]["videoStartHeight"] = videoStartHeight
        print(f"Updated '{currentKey}' to '{videoStartHeight}'")
    else:
        print(f"Key '{currentKey}' not found in the JSON file")

    with open("greWords.json", 'w') as file:
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
                # print(currentSubtitle)
                videoStartHeight = generateImage(currentWord, currentDef, currentSubtitle, index)
                updateJsonFile(currentWord, str(index), videoStartHeight)
                break
        break

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