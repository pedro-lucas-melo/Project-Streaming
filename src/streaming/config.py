import os
from dotenv import load_dotenv


class ConfigManager:
    def __init__(self):
        load_dotenv()
        
        self.media_dir = os.getenv("MEDIA_DIR")
        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", 8080))

        self._validate()

    def _validate(self):
        if not self.media_dir:
            raise ValueError("MEDIA_DIR não definido no .env")

        if not os.path.exists(self.media_dir):
            raise ValueError(f"Diretório de mídia não existe: {self.media_dir}")


if __name__ == "__main__":
    config = ConfigManager()
    print("MEDIA_DIR:", config.media_dir)
    print("HOST:", config.host)
    print("PORT:", config.port)