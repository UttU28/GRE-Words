import os
import json
import re
import sys
from PIL import Image, ImageFont, ImageDraw
import textwrap
from config import (
    JSON_FILE, IMAGES_DIR, BACKGROUND_IMAGE, FONTS_DIR, RESOURCES_DIR,
    WORD_FONT, MEANING_FONT, MOVIE_FONT, DEFAULT_FONT,
    path_str, ensure_dirs_exist
)

# Ensure necessary directories exist
ensure_dirs_exist()

# Load JSON data
with open(path_str(JSON_FILE), "r") as allWords:
    allWordsData = json.load(allWords)

# Check if background image exists
if not os.path.exists(path_str(BACKGROUND_IMAGE)):
    print(f"Error: Background image not found at {path_str(BACKGROUND_IMAGE)}")
    sys.exit(1)

# Font setup with fallbacks
def load_font(font_name, size):
    font_paths = [
        os.path.join(path_str(FONTS_DIR), font_name),  # Local fonts directory
        os.path.join(path_str(RESOURCES_DIR), font_name),  # Resources directory
        font_name                           # System font
    ]
    
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except (IOError, OSError):
            continue
    
    print(f"Warning: Font {font_name} not found, using default font")
    return ImageFont.load_default()

# Load fonts
try:
    # Use the specific font files provided by the user
    wordFont = load_font(WORD_FONT, 75)
    meaningFont = load_font(MEANING_FONT, 50)
    movieFont = load_font(MOVIE_FONT, 40)
    
    # Fallback font for other text elements
    defaultFont = load_font(DEFAULT_FONT, 35)
except Exception as e:
    print(f"Error loading fonts: {e}")
    print(f"Please make sure the required fonts are in the {path_str(FONTS_DIR)} directory.")
    sys.exit(1)

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

def draw_text_with_highlights(draw, text, font, base_color, highlight_color, highlight_word, position, align="center"):
    pattern = re.compile(r'\b' + re.escape(highlight_word.upper()) + r'\b')
    
    if pattern.search(text) is None:
        draw.multiline_text(position, text, fill=base_color, font=font, align=align, anchor="ma")
        return
    
    y_position = position[1]
    for line in text.split('\n'):
        line_width = draw.textlength(line, font=font)
        
        if align == "center":
            x_position = position[0] - line_width/2
        elif align == "left":
            x_position = position[0]
        else:
            x_position = position[0] - line_width
        
        parts = pattern.split(line)
        for i, part in enumerate(parts):
            if part:
                draw.text((x_position, y_position), part, fill=base_color, font=font)
                x_position += draw.textlength(part, font=font)
            
            if i < len(parts) - 1:
                highlight_text = highlight_word.upper()
                
                bold_offsets = [
                    (-1, -1), (-1, 0), (-1, 1),
                    (0, -1),           (0, 1),
                    (1, -1),  (1, 0),  (1, 1)
                ]
                
                for offset_x, offset_y in bold_offsets:
                    draw.text(
                        (x_position + offset_x, y_position + offset_y), 
                        highlight_text, 
                        fill=highlight_color, 
                        font=font
                    )
                
                draw.text(
                    (x_position, y_position), 
                    highlight_text, 
                    fill=highlight_color, 
                    font=font
                )
                
                x_position += draw.textlength(highlight_text, font=font)
        
        y_position += font.getmask("A").getbbox()[3] * 1.5

def generateImage(currentWord, currentDef, currentSubtitle, currentMovie, index, fonts):
    try:
        original_image = Image.open(path_str(BACKGROUND_IMAGE))
        img = original_image.copy()
        draw = ImageDraw.Draw(img)

        # The word itself - using wordFont with increased size and better positioning
        # Center the word vertically and horizontally, and move it higher
        word_color = "#3e2f23"  # Deep Umber for main word
        shadow_offset = 3  # Shadow offset
        
        # Increase font size by loading a larger version of the font
        larger_word_font = fonts["word_large"]  # Increased from 75 to 100
        
        # Calculate position for true center, but at specified y-position
        word_text = currentWord.upper()
        word_position_x = img.width // 2  # Horizontal center of image
        word_position_y = 120  # As modified by user
        
        # Draw shadow first (dark color slightly offset)
        draw.text(
            xy=(word_position_x+shadow_offset, word_position_y+shadow_offset), 
            text=word_text, 
            font=larger_word_font, 
            fill="#333333", 
            anchor="mm"  # "mm" means center of text positioned at the coordinates
        )
        
        # Create bold effect by drawing the text multiple times with tiny offsets
        # This creates a "stroke" effect that makes text appear bolder
        bold_offsets = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1),           (0, 1),
            (1, -1),  (1, 0),  (1, 1)
        ]
        
        # Draw with small offsets first to create bold effect
        for offset_x, offset_y in bold_offsets:
            draw.text(
                xy=(word_position_x+offset_x, word_position_y+offset_y), 
                text=word_text, 
                font=larger_word_font, 
                fill=word_color, 
                anchor="mm"
            )
            
        # Finally draw the main text in the center to fill any gaps
        draw.text(
            xy=(word_position_x, word_position_y), 
            text=word_text, 
            font=larger_word_font, 
            fill=word_color, 
            anchor="mm"
        )

        # The definition - use Antique Gold
        definition_color = "#7a5c39"  # Antique Gold
        
        definition_position_x = img.width // 2  # Horizontal center
        definition_position_y = word_position_y + 120  # Below the main word with spacing
        
        definition_text = currentDef
        
        wrapped_text = getWrappedText(definition_text, fonts["meaning"], img.width - 100)  # Narrower width for better looking paragraphs
        
        draw.multiline_text(
            xy=(definition_position_x, definition_position_y), 
            text=wrapped_text, 
            font=fonts["meaning"], 
            align="center",  # Center-align the text
            fill=definition_color, 
            anchor="ma"  # Top-center anchoring
        )
        
        # Estimate vertical space taken by definition for positioning the movie info
        _, _, _, definition_height = draw.multiline_textbbox(
            (definition_position_x, definition_position_y), 
            wrapped_text, 
            font=fonts["meaning"], 
            align="center", 
            anchor="ma"
        )
        
        # Calculate dynamic positions based on actual content height
        # Add padding after the definition
        definition_bottom = definition_position_y + 100
        padding_after_definition = 80  # Space after definition
        
        # Position movie info below the definition with proper spacing
        movie_info_position = definition_bottom + padding_after_definition
        
        # Set video start position below movie info
        video_padding = 60  # Space between movie info and video
        videoStartHeight = movie_info_position  # We'll adjust this after drawing movie info
        
        # Movie source - use Burgundy
        movie_color = "#88444f"  # Burgundy
        # Position on the left side instead of center
        movie_position_x = 50  # Left margin instead of center
        
        # Wrap movie text if it's too long
        movie_wrapped_text = getWrappedText(currentMovie, fonts["movie"], img.width - 100)
        
        # Draw movie info left-aligned
        draw.multiline_text(
            xy=(movie_position_x, movie_info_position), 
            text=movie_wrapped_text,
            font=fonts["movie"], 
            align="left",  # Left align instead of center
            fill=movie_color
        )
        
        # Calculate height of movie text for positioning the video and subtitle
        _, _, _, movie_text_height = draw.multiline_textbbox(
            (movie_position_x, movie_info_position), 
            movie_wrapped_text, 
            font=fonts["movie"], 
            align="left"  # Match the alignment used above
        )
        
        videoStartHeight = movie_info_position
        
        subtitle_position_y = videoStartHeight + movie_text_height + 120
        
        # Subtitle - use Ox Blood Red
        subtitle_color = "#952e2e"  # Ox Blood Red
        
        # Color for the highlighted word in subtitle - bright gold for contrast
        highlight_color = "#1d1d1d"  # Bright gold
        
        # Find the target word in the subtitle (case insensitive)
        # and prepare a version with the target word capitalized
        highlight_word = currentWord.lower()
        subtitle_text = currentSubtitle
        
        # Function to highlight the target word in the subtitle
        def highlight_word_in_text(text, word_to_highlight):
            # Case insensitive find and replace
            import re
            pattern = re.compile(re.escape(word_to_highlight), re.IGNORECASE)
            return pattern.sub(lambda m: m.group().upper(), text)
        
        # Apply capitalization to the subtitle
        subtitle_text = highlight_word_in_text(subtitle_text, highlight_word)
        
        # Wrap subtitle if needed
        subtitle_wrapped_text = getWrappedText(subtitle_text, fonts["movie"], img.width - 150)
        
        # Use our custom function to draw the subtitle with highlighted words
        draw_text_with_highlights(
            draw, 
            subtitle_wrapped_text, 
            fonts["movie"], 
            subtitle_color,  # Base color
            highlight_color,  # Color for the target word
            highlight_word,  # The word to highlight
            (img.width // 2, subtitle_position_y),  # Position
            "center"  # Alignment
        )

        # Add signature/branding at the bottom of the image
        signature_y = img.height - 180  # Position from bottom
        
        # Main signature - use Walnut Brown
        signature_color = "#5b4332"  # Walnut Brown
        # Main signature text "Wo-Kya-bol-Rahi"
        signature_text = "Wo-Kya-bol-Rahi"
        signature_font = fonts["signature"]  # Using movie font but smaller size
        
        # Draw the main signature text centered horizontally
        draw.text(
            xy=(img.width // 2, signature_y),
            text=signature_text,
            font=signature_font,
            fill=signature_color,
            anchor="mm"  # Center alignment
        )
        
        # Add "vocabulary" text below the signature
        vocabulary_text = "vocabulary"
        vocabulary_font = fonts["vocab"]  # Even smaller for the subtitle
        # Vocabulary text - use Dusty Taupe
        vocabulary_color = "#8e7f71"  # Dusty Taupe
        
        # Draw the vocabulary text centered below the signature
        draw.text(
            xy=(img.width - img.width // 4, signature_y + 45),
            text=vocabulary_text,
            font=vocabulary_font,
            fill=vocabulary_color,
            anchor="mm"  # Center alignment
        )

        # Save the image
        output_path = os.path.join(path_str(IMAGES_DIR), f"{currentWord}{index}.png")
        img.save(output_path, "PNG")
        print(f"Image saved: {output_path}")

        return videoStartHeight
    except Exception as e:
        print(f"Error generating image for {currentWord}: {e}")
        return None

def updateJsonFile(currentKey, currentIndex, videoStartHeight):
    if videoStartHeight is None:
        print(f"Skipping JSON update for {currentKey} due to image generation error")
        return
    
    try:
        with open(path_str(JSON_FILE), 'r') as file:
            data = json.load(file)

        if currentKey in data:
            data[currentKey]["clipData"][currentIndex]["videoStartHeight"] = videoStartHeight
            print(f"Updated '{currentKey}' to '{videoStartHeight}'")
        else:
            print(f"Key '{currentKey}' not found in the JSON file")

        with open(path_str(JSON_FILE), 'w') as file:
            json.dump(data, file, indent=2)
    except Exception as e:
        print(f"Error updating JSON file: {e}")

def upperText(inputString, thisWord):
    pattern = re.compile(r'\b' + re.escape(thisWord) + r'\b', re.IGNORECASE)
    return pattern.sub(thisWord.upper(), inputString)

def make_images_for_word(target_word):
    fonts = {
        "word": wordFont,
        "word_large": load_font(WORD_FONT, 100),
        "meaning": meaningFont,
        "movie": movieFont,
        "default": defaultFont,
        "signature": load_font(MOVIE_FONT, 60),
        "vocab": load_font(MOVIE_FONT, 40)
    }
    
    if target_word not in allWordsData:
        print(f"Word '{target_word}' not found in the database.")
        return False
    
    wordData = allWordsData[target_word]
    currentDef = wordData['meaning']
    print(f"Processing word: {target_word}")
    
    if "clipData" not in wordData or not wordData["clipData"]:
        print(f"No clip data found for {target_word}")
        return False
    
    clips_processed = 0
    for index, videoData in wordData["clipData"].items():
        currentSubtitle = upperText(videoData["subtitle"], target_word)
        currentMovie = videoData["videoInfo"]
        videoStartHeight = generateImage(target_word, currentDef, currentSubtitle, currentMovie, index, fonts)
        updateJsonFile(target_word, str(index), videoStartHeight)
        clips_processed += 1
    
    # Mark word as used
    try:
        with open(path_str(JSON_FILE), 'r') as file:
            data = json.load(file)
        
        if target_word in data:
            data[target_word]["wordUsed"] = True
        
        with open(path_str(JSON_FILE), 'w') as file:
            json.dump(data, file, indent=2)
    except Exception as e:
        print(f"Error updating word usage status: {e}")
    
    print(f"Generated {clips_processed} images for '{target_word}'")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        word = sys.argv[1].lower().strip()
        make_images_for_word(word)
    else:
        word = input("Enter the word to generate images for: ").lower().strip()
        if word:
            make_images_for_word(word)
        else:
            print("No word provided. Exiting.")