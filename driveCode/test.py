import os
import subprocess
import json

def get_video_info(video_file):
    # Run ffprobe to get video information
    result = subprocess.run(['ffprobe', '-v', 'error', '-show_format', '-show_streams', '-print_format', 'json', video_file], capture_output=True)
    
    # Parse the JSON output
    info = json.loads(result.stdout)
    return info

def convert_video(input_file, output_file, video_info):
    # Extract video and audio codec information
    video_codec = video_info['streams'][0]['codec_name']
    audio_codec = video_info['streams'][1]['codec_name']
    
    # Extract video bitrate
    video_bitrate = video_info['streams'][0]['bit_rate']
    
    # Use ffmpeg to convert video to same format
    subprocess.run(['ffmpeg', '-i', input_file, '-c:v', video_codec, '-c:a', audio_codec, '-b:v', str(video_bitrate), output_file])

def merge_videos(video_files, output_file):
    # Create a list of input files for ffmpeg
    input_files = []
    for file in video_files:
        input_files.extend(['-i', file])
    
    # Use ffmpeg to merge videos
    subprocess.run(['ffmpeg', *input_files, '-filter_complex', 'concat=n={}:v=1:a=1'.format(len(video_files)), '-c:v', 'copy', '-c:a', 'copy', output_file])

# Source video file to extract format information
source_video = 'mergedVideos/plummet1.mp4'

# Destination folder for converted videos
output_folder = 'conVieos'
os.makedirs(output_folder, exist_ok=True)

# Get video information from source video
source_info = get_video_info(source_video)

# Convert other video files to same format
video_files_to_convert = ['endVideo.mp4', 'fillerVideo.mp4']
for video_file in video_files_to_convert:
    output_file = os.path.join(output_folder, os.path.basename(video_file))
    convert_video(video_file, output_file, source_info)

# List of converted video files
converted_video_files = [os.path.join(output_folder, file) for file in os.listdir(output_folder)]

# Merge converted videos
output_video = 'merged_video.mp4'
merge_videos(converted_video_files, output_video)
