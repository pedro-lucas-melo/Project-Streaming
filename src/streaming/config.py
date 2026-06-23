import os
from dotenv import load_dotenv


class ConfigManager:
    def __init__(self):
        load_dotenv()
        
        # novas variáveis
        self.media_series_dir = os.getenv("MEDIA_SERIES_DIR")
        self.media_movies_dir = os.getenv("MEDIA_MOVIES_DIR")

        # compatibilidade com código antigo (evita quebrar server atual)
        self.media_dir = self.media_series_dir or self.media_movies_dir

        self.host = os.getenv("HOST", "0.0.0.0")
        self.port = int(os.getenv("PORT", 8080))
        self.tmdb_token = os.getenv("TMDB_API_READ_TOKEN", "")

        self._validate()

    def _validate(self):
        if not self.media_series_dir and not self.media_movies_dir:
            raise ValueError("MEDIA_SERIES_DIR ou MEDIA_MOVIES_DIR não definidos no .env")

        if self.media_series_dir and not os.path.exists(self.media_series_dir):
            raise ValueError(f"Diretório de séries não existe: {self.media_series_dir}")

        if self.media_movies_dir and not os.path.exists(self.media_movies_dir):
            raise ValueError(f"Diretório de filmes não existe: {self.media_movies_dir}")


if __name__ == "__main__":
    config = ConfigManager()
    print("SERIES:", config.media_series_dir)
    print("MOVIES:", config.media_movies_dir)
    print("HOST:", config.host)
    print("PORT:", config.port)