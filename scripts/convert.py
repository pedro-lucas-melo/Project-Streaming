from dotenv import load_dotenv
import os
import subprocess

# carrega .env
load_dotenv()

INPUT_DIR = os.getenv("MEDIA_SOURCE_DIR")
OUTPUT_DIR = os.getenv("MEDIA_DIR")


def convert_video(input_path, output_path):
    command = [
        "ffmpeg",
        "-i", input_path,
        "-c:v", "copy",          # ⚡ copia o vídeo (rápido)
        "-c:a", "aac",           # converte áudio
        "-b:a", "192k",
        "-movflags", "+faststart",  # melhora streaming
        output_path
    ]

    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for root, _, files in os.walk(INPUT_DIR):
        for file in files:
            if file.lower().endswith(".mkv"):
                input_path = os.path.join(root, file)

                relative = os.path.relpath(root, INPUT_DIR)
                output_folder = os.path.join(OUTPUT_DIR, relative)
                os.makedirs(output_folder, exist_ok=True)

                output_file = file.replace(".mkv", ".mp4")
                output_path = os.path.join(output_folder, output_file)

                if os.path.exists(output_path):
                    print(f"Pulando (já existe): {file}")
                    continue

                print(f"Convertendo (rápido): {file}")
                convert_video(input_path, output_path)

    print("\n✅ Conversão finalizada!")


if __name__ == "__main__":
    main()