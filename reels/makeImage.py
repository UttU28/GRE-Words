from PIL import Image, ImageFont, ImageDraw
import textwrap


width, height = 1080, 1920


backgroundColor = "#171A21"
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


    # img.save(f"{currentWord}{index}.png", "PNG")
if __name__ == '__main__':
    # Example usage:
    currentWord = "Apple"
    currentDef = """aapple is a fruit, which is red in color and is very tasty in nature.apple is a fruit, which is red in color and is very tasty in nature.apple is a fruit, which is red in color and is very tasty in nature."""
    currentSubtitle = "This is the current multilined subbtitle, hope you like it"
    generateImage(currentWord, currentDef, currentSubtitle, 0)
