import os
import re
import sys
from PIL import Image, ImageFont, ImageDraw
import textwrap
from tqdm import tqdm
from colorama import init, Fore, Style
from config import (
    IMAGES_DIR, BACKGROUND_IMAGE, FONTS_DIR, RESOURCES_DIR,
    WORD_FONT, MEANING_FONT, MOVIE_FONT, DEFAULT_FONT,
    pathStr, ensureDirsExist
)
from db_controller import db

# Initialize colorama
init(autoreset=True)

# Color formatting functions
def success(text): return f"{Fore.GREEN}{text}{Style.RESET_ALL}"
def error(text): return f"{Fore.RED}{text}{Style.RESET_ALL}"
def info(text): return f"{Fore.CYAN}{text}{Style.RESET_ALL}"
def warning(text): return f"{Fore.YELLOW}{text}{Style.RESET_ALL}"
def highlight(text): return f"{Fore.MAGENTA}{Style.BRIGHT}{text}{Style.RESET_ALL}"

ensureDirsExist()

if not os.path.exists(pathStr(BACKGROUND_IMAGE)):
    print(error(f"Error: Background image not found at {pathStr(BACKGROUND_IMAGE)}"))
    sys.exit(1)

def loadFont(fontName, size):
    fontPaths = [
        os.path.join(pathStr(FONTS_DIR), fontName),
        os.path.join(pathStr(RESOURCES_DIR), fontName),
        fontName
    ]
    
    for path in fontPaths:
        try:
            return ImageFont.truetype(path, size)
        except (IOError, OSError):
            continue
    
    print(warning(f"Warning: Font {fontName} not found, using default font"))
    return ImageFont.load_default()

try:
    wordFont = loadFont(WORD_FONT, 75)
    meaningFont = loadFont(MEANING_FONT, 50)
    movieFont = loadFont(MOVIE_FONT, 40)
    
    defaultFont = loadFont(DEFAULT_FONT, 35)
except Exception as e:
    print(error(f"Error loading fonts: {e}"))
    print(error(f"Please make sure the required fonts are in the {pathStr(FONTS_DIR)} directory."))
    sys.exit(1)

def hex2Rgb(rgbColor):
    return tuple(int(rgbColor[i:i+2], 16) for i in (1, 3, 5))

def getWrappedText(text: str, font: ImageFont.ImageFont, lineLength: int):
    lines = ['']
    for word in text.split():
        line = f'{lines[-1]} {word}'.strip()
        if font.getlength(line) <= lineLength:
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

def drawTextWithHighlights(draw, text, font, baseColor, highlightColor, highlightWord, position, align="center"):
    pattern = re.compile(r'\b' + re.escape(highlightWord.upper()) + r'\b')
    
    if pattern.search(text) is None:
        draw.multiline_text(position, text, fill=baseColor, font=font, align=align, anchor="ma")
        return
    
    yPosition = position[1]
    for line in text.split('\n'):
        lineWidth = draw.textlength(line, font=font)
        
        if align == "center":
            xPosition = position[0] - lineWidth/2
        elif align == "left":
            xPosition = position[0]
        else:
            xPosition = position[0] - lineWidth
        
        parts = pattern.split(line)
        for i, part in enumerate(parts):
            if part:
                draw.text((xPosition, yPosition), part, fill=baseColor, font=font)
                xPosition += draw.textlength(part, font=font)
            
            if i < len(parts) - 1:
                highlightText = highlightWord.upper()
                
                boldOffsets = [
                    (-1, -1), (-1, 0), (-1, 1),
                    (0, -1),           (0, 1),
                    (1, -1),  (1, 0),  (1, 1)
                ]
                
                for offsetX, offsetY in boldOffsets:
                    draw.text(
                        (xPosition + offsetX, yPosition + offsetY), 
                        highlightText, 
                        fill=highlightColor, 
                        font=font
                    )
                
                draw.text(
                    (xPosition, yPosition), 
                    highlightText, 
                    fill=highlightColor, 
                    font=font
                )
                
                xPosition += draw.textlength(highlightText, font=font)
        
        yPosition += font.getmask("A").getbbox()[3] * 1.5

def generateImage(currentWord, currentDef, currentSubtitle, currentMovie, index, fonts):
    try:
        originalImage = Image.open(pathStr(BACKGROUND_IMAGE))
        img = originalImage.copy()
        draw = ImageDraw.Draw(img)

        wordColor = "#3e2f23"
        shadowOffset = 3
        
        largerWordFont = fonts["word_large"]
        
        wordText = currentWord.upper()
        wordPositionX = img.width // 2
        wordPositionY = 120
        
        draw.text(
            xy=(wordPositionX+shadowOffset, wordPositionY+shadowOffset), 
            text=wordText, 
            font=largerWordFont, 
            fill="#333333", 
            anchor="mm"
        )
        
        boldOffsets = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        
        for offsetX, offsetY in boldOffsets:
            draw.text(
                xy=(wordPositionX+offsetX, wordPositionY+offsetY), 
                text=wordText, 
                font=largerWordFont, 
                fill=wordColor, 
                anchor="mm"
            )
            
        draw.text(
            xy=(wordPositionX, wordPositionY), 
            text=wordText, 
            font=largerWordFont, 
            fill=wordColor, 
            anchor="mm"
        )

        definitionColor = "#7a5c39"
        
        definitionPositionX = img.width // 2
        definitionPositionY = wordPositionY + 120
        
        definitionText = currentDef
        
        wrappedText = getWrappedText(definitionText, fonts["meaning"], img.width - 100)
        
        draw.multiline_text(
            xy=(definitionPositionX, definitionPositionY), 
            text=wrappedText, 
            font=fonts["meaning"], 
            align="center",
            fill=definitionColor, 
            anchor="ma"
        )
        
        _, _, _, definitionHeight = draw.multiline_textbbox(
            (definitionPositionX, definitionPositionY), 
            wrappedText, 
            font=fonts["meaning"], 
            align="center", 
            anchor="ma"
        )
        
        definitionBottom = definitionHeight + 50
        
        videoPadding = 60
        videoStartHeight = definitionBottom
        
        movieColor = "#88444f"
        moviePositionX = 50
        
        movieWrappedText = getWrappedText(currentMovie, fonts["movie"], img.width - 100)
        
        draw.multiline_text(
            xy=(moviePositionX, definitionBottom), 
            text=movieWrappedText,
            font=fonts["movie"], 
            align="left",
            fill=movieColor
        )
        
        _, _, _, movieTextHeight = draw.multiline_textbbox(
            (moviePositionX, definitionBottom), 
            movieWrappedText, 
            font=fonts["movie"], 
            align="left"
        )
        
        videoStartHeight = definitionBottom
        
        subtitlePositionY = videoStartHeight + movieTextHeight + 220
        
        subtitleColor = "#952e2e"
        
        highlightColor = "#1d1d1d"
        
        highlightWord = currentWord.lower()
        subtitleText = currentSubtitle
        
        def highlightWordInText(text, wordToHighlight):
            import re
            pattern = re.compile(re.escape(wordToHighlight), re.IGNORECASE)
            return pattern.sub(lambda m: m.group().upper(), text)
        
        subtitleText = highlightWordInText(subtitleText, highlightWord)
        
        subtitleWrappedText = getWrappedText(subtitleText, fonts["movie"], img.width - 150)
        
        drawTextWithHighlights(
            draw, 
            subtitleWrappedText, 
            fonts["movie"], 
            subtitleColor,
            highlightColor,
            highlightWord,
            (img.width // 2, subtitlePositionY),
            "center"
        )

        signatureY = img.height - 180
        
        signatureColor = "#5b4332"
        signatureText = "Wo-Kya-bol-Rahi"
        signatureFont = fonts["signature"]
        
        draw.text(
            xy=(img.width // 2, signatureY),
            text=signatureText,
            font=signatureFont,
            fill=signatureColor,
            anchor="mm"
        )
        
        vocabularyText = "vocabulary"
        vocabularyFont = fonts["vocab"]
        vocabularyColor = "#8e7f71"
        
        draw.text(
            xy=(img.width - img.width // 4, signatureY + 45),
            text=vocabularyText,
            font=vocabularyFont,
            fill=vocabularyColor,
            anchor="mm"
        )

        outputPath = os.path.join(pathStr(IMAGES_DIR), f"{currentWord}{index}.png")
        img.save(outputPath, "PNG")

        return videoStartHeight
    except Exception as e:
        print(error(f"Error generating image for {currentWord}: {e}"))
        return None

def updateVideoStartHeight(word, clipIndex, videoStartHeight):
    if videoStartHeight is None:
        return
    
    try:
        wordRow = db.getWord(word)
        if not wordRow:
            return
            
        wordId = wordRow['id']
        
        db.updateClipVideoStartHeightByIndex(wordId, int(clipIndex), videoStartHeight)
    except Exception as e:
        print(error(f"Error updating database: {e}"))

def upperText(inputString, thisWord):
    pattern = re.compile(r'\b' + re.escape(thisWord) + r'\b', re.IGNORECASE)
    return pattern.sub(thisWord.upper(), inputString)

def makeImagesForWord(targetWord):
    fonts = {
        "word": wordFont,
        "word_large": loadFont(WORD_FONT, 100),
        "meaning": meaningFont,
        "movie": movieFont,
        "default": defaultFont,
        "signature": loadFont(MOVIE_FONT, 60),
        "vocab": loadFont(MOVIE_FONT, 40)
    }
    
    wordRow = db.getWord(targetWord)
    if not wordRow:
        print(error(f"Word '{targetWord}' not found in the database."))
        return False
    
    wordId = wordRow['id']
    currentDef = wordRow['meaning']
    
    clips = db.getClipsForWord(wordId)
    if not clips:
        print(warning(f"No clip data found for {targetWord}"))
        return False
    
    clipsProcessed = 0
    progressBar = tqdm(clips, desc=f"Generating images for: {targetWord.upper()}", unit="image")
    for clip in progressBar:
        index = clip['clip_index']
        currentSubtitle = upperText(clip['subtitle'], targetWord)
        currentMovie = clip['video_info']
        videoStartHeight = generateImage(targetWord, currentDef, currentSubtitle, currentMovie, index, fonts)
        updateVideoStartHeight(targetWord, index, videoStartHeight)
        clipsProcessed += 1
    
    print(success(f"Generated {clipsProcessed} images for '{targetWord}'"))
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        word = sys.argv[1].lower().strip()
        makeImagesForWord(word)
    else:
        word = "nuance"
        if word:
            makeImagesForWord(word)
        else:
            print(error("No word provided. Exiting."))