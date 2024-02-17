from PIL import Image, ImageDraw, ImageFont

def getWrappedText(text: str, font: ImageFont.ImageFont, line_length: int):
    lines = ['']
    for word in text.split():
        line = f'{lines[-1]} {word}'.strip()
        if font.getlength(line) <= line_length:
            lines[-1] = line
        else:
            lines.append(word)
    return '\n'.join(lines)

def imageTextGenerator(draw, text, textSpacing, fontPath, paddingTop):
    maxFontWidth = 1080 - 100
    maxFontHeight = 1920 - 100
    finalMultilineText = ""
    finalTitleFont = None
    titleFont = ImageFont.truetype(fontPath, size=50)
    multilineText = getWrappedText(text, titleFont, maxFontWidth)
    _, _, w, h = draw.multiline_textbbox((0, 0), multilineText, font=titleFont, spacing=textSpacing)
    if not (w > maxFontWidth or h > maxFontHeight):
        finalMultilineText = multilineText
        finalTitleFont = titleFont

    x = 50 + (1080 - 100) / 2
    y = paddingTop
    return finalMultilineText, finalTitleFont, x, y

if __name__ == "__main__":
    backgroundImagePath = "image.png"
    backgroundImage = Image.open(backgroundImagePath)
    draw = ImageDraw.Draw(backgroundImage)

    text = "The Best Way To Get Started Is To Quit Talking And Begin Doing."
    quoteSpacing = 12
    fontPath = "Roboto-Black.ttf"

    paddingTop = 700 + 538
    multilineText, font, positionX, positionY = imageTextGenerator(draw, text, quoteSpacing, fontPath, paddingTop)
    draw.multiline_text(xy=(positionX, positionY), text=multilineText, font=font, align="center", spacing=quoteSpacing, fill="white", anchor="ma")
    backgroundImage.show()
    # backgroundImage.save("output_image.jpg")
