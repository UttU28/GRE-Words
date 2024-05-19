# GRE-Words
Making Video using GRE Words and Extracting Video from PlayPhrase.me

ffmpeg -i endVideo.mp4 -i thisAudio.mp3 -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest oendVideo.mp4
