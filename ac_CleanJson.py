import json
import os
import sys
from collections import defaultdict
from utils import error, info, success

def clean_json(input_file=None, output_file=None):
    if input_file is None:
        input_file = os.path.join("resources", "greWords.json")
    
    if not os.path.exists(input_file):
        print(error(f"Error: Input file '{input_file}' not found"))
        return False
    
    if output_file is None:
        base, ext = os.path.splitext(input_file)
        output_file = f"{base}_cleaned{ext}"
    
    print(info(f"Reading JSON file: {input_file}"))
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(error(f"Error parsing JSON: {e}"))
        return False
    except Exception as e:
        print(error(f"Error reading file: {e}"))
        return False
    
    word_count = 0
    duplicate_count = 0
    short_subtitle_count = 0
    
    for word, word_data in data.items():
        if "clipData" not in word_data:
            continue
        
        seen_urls = set()
        clips_to_remove = []
        
        for clip_id, clip_info in word_data["clipData"].items():
            remove_clip = False
            
            if "videoURL" in clip_info:
                video_url = clip_info["videoURL"]
                if video_url in seen_urls:
                    remove_clip = True
                    duplicate_count += 1
                else:
                    seen_urls.add(video_url)
            
            if "subtitle" in clip_info:
                subtitle = clip_info["subtitle"]
                word_count_in_subtitle = len(subtitle.split())
                if word_count_in_subtitle < 4:
                    remove_clip = True
                    short_subtitle_count += 1
                    print(f"Removing clip for '{word}' with short subtitle: '{subtitle}' ({word_count_in_subtitle} words)")
            
            if remove_clip:
                clips_to_remove.append(clip_id)
        
        for clip_id in clips_to_remove:
            del word_data["clipData"][clip_id]
        
        if clips_to_remove:
            word_data["clipsFound"] = len(word_data["clipData"])
            word_count += 1
    
    print(f"Found and removed {duplicate_count} duplicate video URLs across {word_count} words")
    print(f"Found and removed {short_subtitle_count} clips with fewer than 4 words in subtitle")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(success(f"Cleaned JSON saved to: {output_file}"))
        return True
    except Exception as e:
        print(error(f"Error writing output file: {e}"))
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        clean_json(input_file, output_file)
    else:
        default_output = os.path.join("resources", "words_cleaned.json")
        clean_json(output_file=default_output)
