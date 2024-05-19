import requests
import os

def download_file(url, filename):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print(f"Downloaded {filename}")
    else:
        print(f"Failed to download {filename}")

def merge_audio_video(video_file, audio_file, output_file):
    command = f"ffmpeg -i {video_file} -i {audio_file} -c:v copy -c:a aac {output_file}"
    os.system(command)
    print(f"Merged video saved as {output_file}")

# URLs for the video and audio streams (example, modify if necessary)
video_url = "https://s3.us-west-1.wasabisys.com/video-us.playphrase.me/english-storage/5b96add2cc77853d88561744/628b88deb071e717a65fa251.mp4"
audio_url = "https://example.com/audio-file.mp4"  # Replace with actual audio URL if different

# Filenames for the downloaded video and audio
video_file = "video.mp4"
audio_file = "audio.mp4"
output_file = "output.mp4"

# Download video and audio streams
download_file(video_url, video_file)
download_file(audio_url, audio_file)

# Merge video and audio streams
merge_audio_video(video_file, audio_file, output_file)
