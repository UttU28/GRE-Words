import os
import subprocess
import contextlib
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm
from colorama import init, Fore, Style
from config import (
    FONTS_DIR, IMAGES_DIR, BACKGROUND_IMAGE, MERGED_VIDEOS_DIR,
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

# Image file paths
INTRO_IMAGE_PATH = os.path.join(pathStr(IMAGES_DIR), "intro.png")
OUTRO_IMAGE_PATH = os.path.join(pathStr(IMAGES_DIR), "outro.png")

# Video file paths
INTRO_VIDEO_PATH = os.path.join(pathStr(MERGED_VIDEOS_DIR), "intro.mp4")
OUTRO_VIDEO_PATH = os.path.join(pathStr(MERGED_VIDEOS_DIR), "outro.mp4")

# Font and color setup
FONTS = {
    "title": None,
    "vocabulary": None,
    "subtitle": None,
    "cta": None,
    "today_word": None,
    "featured_word": None
}

COLORS = {
    "title": "#3e2f23",
    "vocabulary": "#8e7f71",
    "subtitle": "#7a5c39",
    "cta": "#7a5c39",
    "word": "#452d17"
}

LINE_SPACING = 1.3
BOLD_OFFSETS = [
    (-2, -2), (-2, 0), (-2, 2),
    (0, -2),           (0, 2),
    (2, -2),  (2, 0),  (2, 2)
]

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

# Image creation functions
def loadFont(fontName, size):
    fontPaths = [
        os.path.join(pathStr(FONTS_DIR), fontName),
        os.path.join(pathStr(IMAGES_DIR), fontName),
        fontName
    ]
    
    for path in fontPaths:
        try:
            return ImageFont.truetype(path, size)
        except (IOError, OSError):
            continue
    
    print(warning(f"Warning: Font {fontName} not found, using default font"))
    return ImageFont.load_default()

def loadFonts():
    FONTS["title"] = loadFont("Word.ttf", 90)
    FONTS["vocabulary"] = loadFont("Movie.ttf", 52)
    FONTS["subtitle"] = loadFont("Meaning.ttf", 50) 
    FONTS["cta"] = loadFont("Movie.ttf", 50)
    FONTS["today_word"] = loadFont("Meaning.ttf", 45)
    FONTS["featured_word"] = loadFont("Word.ttf", 75)

def getWrappedText(draw, text, font, maxWidth):
    lines = []
    words = text.split()
    currentLine = words[0]
    
    for word in words[1:]:
        testLine = currentLine + " " + word
        lineWidth = draw.textlength(testLine, font=font)
        
        if lineWidth <= maxWidth:
            currentLine = testLine
        else:
            lines.append(currentLine)
            currentLine = word
            
    lines.append(currentLine)
    return "\n".join(lines)

def drawBoldText(draw, text, x, y, font, color, anchor="mm"):
    for offsetX, offsetY in BOLD_OFFSETS:
        draw.text(
            xy=(x+offsetX, y+offsetY), 
            text=text, 
            font=font, 
            fill=color, 
            anchor=anchor
        )
    
    draw.text(
        xy=(x, y), 
        text=text, 
        font=font, 
        fill=color, 
        anchor=anchor
    )

def drawMultilineText(draw, text, x, y, font, color, maxWidth, align="center"):
    wrappedText = getWrappedText(draw, text, font, maxWidth)
    
    spacing = int(font.size * LINE_SPACING - font.size)
    
    draw.multiline_text(
        xy=(x, y), 
        text=wrappedText, 
        font=font, 
        fill=color, 
        align=align,
        anchor="ma",
        spacing=spacing
    )
    
    return wrappedText

def drawTitleAndVocabulary(draw, width, titleY):
    centerX = width // 2
    
    titleText = "Wo-Kya-bol-Rahi"
    drawBoldText(draw, titleText, centerX, titleY, FONTS["title"], COLORS["title"])
    
    vocabText = "vocabulary"
    vocabY = titleY + 65
    vocabX = centerX + 240
    
    vocabColorWithAlpha = COLORS["vocabulary"] + "CC"
    
    draw.text(
        xy=(vocabX, vocabY), 
        text=vocabText, 
        font=FONTS["vocabulary"], 
        fill=vocabColorWithAlpha, 
        anchor="mm"
    )
    
    return centerX

def drawFooter(draw, centerX, height, maxWidth):
    ctaY = height - 250
    
    footerData = {
        "intro": "Check BIO for YouTube!",
        "outro": "Follow for more GRE vocabulary"
    }
    
    return footerData, ctaY

def createIntroImage(word):
    originalImage = Image.open(pathStr(BACKGROUND_IMAGE))
    img = originalImage.copy()
    draw = ImageDraw.Draw(img)
    
    width, height = img.size
    titleY = height // 6
    centerX = drawTitleAndVocabulary(draw, width, titleY)
    
    maxWidth = width - 100
    
    taglineText = "Sharpening your English vocab with Movies & Shows clips... One word at a time!!"
    taglineY = titleY + 150
    
    wrappedTagline = drawMultilineText(
        draw, taglineText, centerX, taglineY,
        FONTS["subtitle"], COLORS["subtitle"], maxWidth
    )
    
    _, _, _, taglineHeight = draw.multiline_textbbox(
        (centerX, taglineY), 
        wrappedTagline,
        font=FONTS["subtitle"],
        anchor="ma",
        align="center",
        spacing=int(FONTS["subtitle"].size * LINE_SPACING - FONTS["subtitle"].size)
    )
    
    todaysWordText = "Today's word:"
    todaysWordY = taglineY + taglineHeight//2 + 50
    
    draw.text(
        xy=(centerX, todaysWordY), 
        text=todaysWordText, 
        font=FONTS["today_word"], 
        fill=COLORS["subtitle"], 
        anchor="mm"
    )
    
    wordText = word.upper()
    wordY = todaysWordY + 70
    
    drawBoldText(draw, wordText, centerX, wordY, FONTS["featured_word"], COLORS["word"])
    
    footerData, ctaY = drawFooter(draw, centerX, height, maxWidth)
    
    ctaText = footerData["intro"]
    drawMultilineText(
        draw, ctaText, centerX, ctaY,
        FONTS["cta"], COLORS["cta"], maxWidth
    )
    
    handleText = "@wokyabolrahi"
    handleY = ctaY + 80
    
    draw.text(
        xy=(centerX, handleY), 
        text=handleText, 
        font=FONTS["cta"], 
        fill=COLORS["cta"], 
        anchor="mm"
    )
    
    img.save(INTRO_IMAGE_PATH)
    return INTRO_IMAGE_PATH

def createOutroImage():
    originalImage = Image.open(pathStr(BACKGROUND_IMAGE))
    img = originalImage.copy()
    draw = ImageDraw.Draw(img)
    
    width, height = img.size
    titleY = height // 6
    centerX = drawTitleAndVocabulary(draw, width, titleY)
    
    maxWidth = width - 100
    
    thanksText1 = "Thanks for watching!"
    thanksY1 = titleY + 200
    
    draw.text(
        xy=(centerX, thanksY1), 
        text=thanksText1, 
        font=FONTS["subtitle"], 
        fill=COLORS["subtitle"], 
        anchor="mm"
    )
    
    thanksText2 = "Check BIO for YouTube!"
    thanksY2 = thanksY1 + FONTS["subtitle"].size + 20
    
    draw.text(
        xy=(centerX, thanksY2), 
        text=thanksText2, 
        font=FONTS["subtitle"], 
        fill=COLORS["subtitle"], 
        anchor="mm"
    )
    
    youtubeLabel = "YouTube:"
    youtubeLabelY = thanksY2 + FONTS["subtitle"].size + 150
    
    draw.text(
        xy=(centerX, youtubeLabelY), 
        text=youtubeLabel, 
        font=FONTS["today_word"], 
        fill=COLORS["subtitle"], 
        anchor="mm"
    )
    
    channelName = "ThatInsaneGuy"
    channelY = youtubeLabelY + 70
    
    drawBoldText(
        draw, 
        channelName, 
        centerX, 
        channelY, 
        FONTS["featured_word"], 
        COLORS["word"],
        anchor="mm"
    )
    
    footerData, ctaY = drawFooter(draw, centerX, height, maxWidth)
    
    ctaText = footerData["outro"]
    drawMultilineText(
        draw, ctaText, centerX, ctaY,
        FONTS["cta"], COLORS["cta"], maxWidth
    )
    
    handleText = "@wokyabolrahi"
    handleY = ctaY + 80
    
    draw.text(
        xy=(centerX, handleY), 
        text=handleText, 
        font=FONTS["cta"], 
        fill=COLORS["cta"], 
        anchor="mm"
    )
    
    img.save(OUTRO_IMAGE_PATH)
    return OUTRO_IMAGE_PATH

# Video creation functions
def createVideoFromImage(imageLocation, outputLocation, duration, fadeIn=False, fadeOut=False):
    filterComplex = []
    
    if fadeIn and fadeOut:
        filterComplex = [
            'fade=t=in:st=0:d=1',
            'fade=t=out:st=' + str(duration-1) + ':d=1'
        ]
    elif fadeIn:
        filterComplex = ['fade=t=in:st=0:d=1']
    elif fadeOut:
        filterComplex = ['fade=t=out:st=' + str(duration-1) + ':d=1']
        
    filterStr = ','.join(filterComplex) if filterComplex else 'null'
    
    ffmpegCommand = [
        'ffmpeg',
        '-loop', '1',
        '-i', imageLocation,
        '-f', 'lavfi',
        '-i', 'anullsrc=r=44100:cl=stereo',
        '-t', str(duration),
        '-vf', filterStr,
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-ar', '44100',
        '-ac', '2',
        '-shortest',
        '-tune', 'stillimage',
        '-pix_fmt', 'yuv420p',
        '-y', outputLocation
    ]
    
    try:
        with SuppressOutput():
            subprocess.run(ffmpegCommand, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        return False

# Main process function
def createIntroOutroVideos(word):
    # Track progress in steps
    steps = [
        {"name": "Loading fonts", "func": loadFonts},
        {"name": "Creating intro image", "func": lambda: createIntroImage(word)},
        {"name": "Creating outro image", "func": createOutroImage},
        {"name": "Creating intro video", "func": lambda: createVideoFromImage(INTRO_IMAGE_PATH, INTRO_VIDEO_PATH, 3, fadeIn=True, fadeOut=False)},
        {"name": "Creating outro video", "func": lambda: createVideoFromImage(OUTRO_IMAGE_PATH, OUTRO_VIDEO_PATH, 5, fadeIn=False, fadeOut=True)}
    ]
    
    progressBar = tqdm(steps, desc=f"Creating intro/outro for: {word.upper()}", unit="step")
    
    successful = 0
    for step in progressBar:
        result = step["func"]()
        if result is not False:  # Some functions return None, which should count as success
            successful += 1
    
    if successful == len(steps):
        print(success(f"Successfully created intro/outro videos for {word}"))
        return True
    else:
        print(warning(f"Created {successful}/{len(steps)} intro/outro elements"))
        return False

if __name__ == "__main__":
    wordInput = "abate"
    createIntroOutroVideos(wordInput) 