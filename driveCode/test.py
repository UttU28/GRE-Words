#!/usr/bin/env python3

import sys
import subprocess

def merge_videos(output_file, *input_files):
    # Construct filter_complex string dynamically
    filter_complex = ''.join(f'[{i}:v][{i}:a]' for i in range(len(input_files)))
    map_args = ''.join(f'[{i}:a]' for i in range(len(input_files)))

    filter_complex += f"concat=n={len(input_files)}:v=1:a=1[outv][outa]"


    # Run ffmpeg command
    command = [
        "ffmpeg",
        "-hide_banner",
        "-i",
        *input_files,
        "-filter_complex",
        filter_complex,
        "-map",
        "[outv]",
        "-map",
        map_args,
        "-c:v",
        "libx264",
        "-c:a",
        "aac",
        output_file
    ]
    subprocess.run(command)

if __name__ == "__main__":
    output_file = "out.mp4"
    input_files = ["mergedVideos/plummet1.mp4","ofillerVideo.mp4","mergedVideos/plummet2.mp4","ofillerVideo.mp4","mergedVideos/plummet3.mp4","ofillerVideo.mp4","mergedVideos/plummet4.mp4","oendVideo.mp4"]
    merge_videos(output_file, *input_files)
