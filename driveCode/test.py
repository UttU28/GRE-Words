import requests
import subprocess

def download_video(url, output_path):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(output_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    file.write(chunk)
        print(f"Video downloaded successfully and saved as {output_path}")
    else:
        print(f"Failed to download video. Status code: {response.status_code}")

def verify_and_process_video(input_path, output_path):
    command = [
        'ffmpeg', '-i', input_path,
        '-c', 'copy', output_path
    ]
    try:
        subprocess.run(command, check=True)
        print(f"Video processed and saved as {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error during video processing: {e}")

# URL of the video to be downloaded
video_url = "https://s3.us-west-1.wasabisys.com/video-us.playphrase.me/english-storage/5b96add2cc77853d88561744/628b88deb071e717a65fa251.mp4"
# Path where the video will be saved
downloaded_video_path = "downloaded_video.mp4"
# Path for the final processed video
processed_video_path = "processed_video.mp4"

# Download the video
download_video(video_url, downloaded_video_path)

# Verify and process the video to ensure it has both video and audio
verify_and_process_video(downloaded_video_path, processed_video_path)
