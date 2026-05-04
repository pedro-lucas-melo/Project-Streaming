import os


class MediaLibrary:
    SUPPORTED_EXTENSIONS = (".mp4", ".mkv")

    def __init__(self, media_dir: str):
        self.media_dir = media_dir

    def list_videos(self):
        videos = []

        for root, _, files in os.walk(self.media_dir):
            for file in files:
                if file.lower().endswith(self.SUPPORTED_EXTENSIONS):
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, self.media_dir)

                    videos.append({
                        "name": file,
                        "path": full_path,
                        "relative_path": relative_path
                    })

        return videos

if __name__ == "__main__":
    from streaming.config import ConfigManager

    config = ConfigManager()
    library = MediaLibrary(config.media_dir)

    videos = library.list_videos()

    for v in videos:
        print(v)