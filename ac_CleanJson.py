import json
import os
import sys
from collections import defaultdict
from utils import error, info, success

def cleanJson(inputFile=None, outputFile=None):
    if inputFile is None:
        inputFile = os.path.join("resources", "greWords.json")
    
    if not os.path.exists(inputFile):
        print(error(f"❌ Input file '{inputFile}' not found"))
        return False
    
    if outputFile is None:
        base, ext = os.path.splitext(inputFile)
        outputFile = f"{base}_cleaned{ext}"
    
    print(info(f"📖 Reading JSON file: {inputFile}"))
    
    try:
        with open(inputFile, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(error(f"❌ Error parsing JSON: {e}"))
        return False
    except Exception as e:
        print(error(f"❌ Error reading file: {e}"))
        return False
    
    wordCount = 0
    duplicateCount = 0
    shortSubtitleCount = 0
    
    for word, wordData in data.items():
        if "clipData" not in wordData:
            continue
        
        seenUrls = set()
        clipsToRemove = []
        
        for clipId, clipInfo in wordData["clipData"].items():
            removeClip = False
            
            if "videoURL" in clipInfo:
                videoUrl = clipInfo["videoURL"]
                if videoUrl in seenUrls:
                    removeClip = True
                    duplicateCount += 1
                else:
                    seenUrls.add(videoUrl)
            
            if "subtitle" in clipInfo:
                subtitle = clipInfo["subtitle"]
                wordCountInSubtitle = len(subtitle.split())
                if wordCountInSubtitle < 4:
                    removeClip = True
                    shortSubtitleCount += 1
                    print(f"🗑️  Removing clip for '{word}' with short subtitle: '{subtitle}' ({wordCountInSubtitle} words)")
            
            if removeClip:
                clipsToRemove.append(clipId)
        
        for clipId in clipsToRemove:
            del wordData["clipData"][clipId]
        
        if clipsToRemove:
            wordData["clipsFound"] = len(wordData["clipData"])
            wordCount += 1
    
    print(f"🔄 Removed {duplicateCount} duplicate URLs across {wordCount} words")
    print(f"🔄 Removed {shortSubtitleCount} clips with < 4 words in subtitle")
    
    try:
        with open(outputFile, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(success(f"✅ Cleaned JSON saved to: {outputFile}"))
        return True
    except Exception as e:
        print(error(f"❌ Error writing output file: {e}"))
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        inputFile = sys.argv[1]
        outputFile = sys.argv[2] if len(sys.argv) > 2 else None
        cleanJson(inputFile, outputFile)
    else:
        defaultOutput = os.path.join("resources", "words_cleaned.json")
        cleanJson(outputFile=defaultOutput)
