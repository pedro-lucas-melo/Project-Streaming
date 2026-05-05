import subprocess

FILE = r"C:\Users\PedroMelo\Documents\Projeto Streaming\videos\Mr Robot\Temporada 2\E12 - d3bug_like_a_girl.deb.mkv"
OUTPUT = r"C:\Users\PedroMelo\Documents\Projeto Streaming\videos_converted\Mr Robot\Temporada 2\E12 - d3bug_like_a_girl.deb.mp4"

import os
os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

command = [
    "ffmpeg",
    "-i", FILE,
    "-c:v", "copy",
    "-c:a", "aac",
    "-b:a", "192k",
    "-movflags", "+faststart",
    OUTPUT
]

print("Convertendo E12...")
subprocess.run(command)
print("✅ Pronto!")