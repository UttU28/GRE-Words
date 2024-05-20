# GRE-Words
Making Video using GRE Words and Extracting Video from PlayPhrase.me

ffmpeg -loop 1 -i videoResources/woKyaBolRahiFiller.png -c:v libx264 -t 1 -vf "scale=1920:1080" -pix_fmt yuv420p fillerVideo.mp4

ffmpeg -loop 1 -i videoResources/woKyaBolRahiEnd.png -c:v libx264 -t 3 -vf "scale=1920:1080" -pix_fmt yuv420p endVideo.mp4


ffmpeg -i fillerVideo.mp4 -i thisAudio.mp3 -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest ofillerVideo.mp4

ffmpeg -i endVideo.mp4 -i thisAudio.mp3 -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 -shortest oendVideo.mp4

ffmpeg -f concat -i input.txt -vf "fps=30,scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2" -b:v 2M -c:a copy output.mp4
