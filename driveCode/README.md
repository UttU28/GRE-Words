# GRE-Words
Making Video using GRE Words and Extracting Video from PlayPhrase.me

ffmpeg -i input_video.mp4 -i input_audio.mp3 -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest output_video.mp4
