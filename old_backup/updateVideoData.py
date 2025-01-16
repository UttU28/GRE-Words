import json
import os
import moviepy.editor as mp

def readJsonFile(jsonFile):
    with open(jsonFile, 'r') as f:
        data = json.load(f)
    return data

def writeJsonFile(data, jsonFile):
    with open(jsonFile, 'w') as f:
        json.dump(data, f, indent=4)

def findUnaddedAndRejectedVideos(uploadData, folderPath):
    addedVideos = uploadData.get('addedVideos', [])
    unaddedVideos = uploadData.get('unaddedVideos', [])
    rejectedVideos = uploadData.get('rejectedVideos', [])
    allVideos = []
    
    for root, dirs, files in os.walk(folderPath):
        for file in files:
            if file.endswith('.mp4'):  # Adjust file extension if needed
                videoPath = os.path.join(root, file)
                allVideos.append(videoPath)
    
    for videoPath in allVideos:
        if videoPath not in addedVideos and videoPath not in unaddedVideos:
            # Check video duration
            clip = mp.VideoFileClip(videoPath)
            duration = clip.duration
            print(f"Duration of {videoPath}: {duration} seconds")
            clip.close()
            
            if duration < 25:
                rejectedVideos.append(videoPath)
            else:
                unaddedVideos.append(videoPath)
    
    # Update upload data with new unadded and rejected videos
    uploadData['unaddedVideos'] = unaddedVideos
    uploadData['rejectedVideos'] = rejectedVideos
    
    # Write updated data back to JSON file
    writeJsonFile(uploadData, jsonFile)

    return unaddedVideos, rejectedVideos

# Read uploadData.json
jsonFile = 'uploadData.json'
uploadData = readJsonFile(jsonFile)

# Find unadded and rejected videos in the folder 'reelsCode/finalVideos'
folderPath = 'reelsCode/finalVideos'
unaddedVideos, rejectedVideos = findUnaddedAndRejectedVideos(uploadData, folderPath)

print("Unadded Videos:")
for video in unaddedVideos:
    print(video)

print("\nRejected Videos:")
for video in rejectedVideos:
    print(video)

print("\nuploadData.json has been updated with the new unadded and rejected videos.")
