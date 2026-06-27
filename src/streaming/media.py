import os


class MediaLibrary:
    SUPPORTED_EXTENSIONS = (".mp4", ".mkv")

    def __init__(self, media_dir: str):
        self.media_dir = media_dir
        self._structure_cache: dict | None = None

    def list_videos(self) -> list[dict]:
        videos = []
        for root, _, files in os.walk(self.media_dir):
            for file in files:
                if file.lower().endswith(self.SUPPORTED_EXTENSIONS):
                    full_path = os.path.join(root, file)
                    relative_path = os.path.relpath(full_path, self.media_dir)
                    videos.append({
                        "name": file,
                        "path": full_path,
                        "relative_path": relative_path,
                    })
        return videos

    def get_structure(self, refresh: bool = False) -> dict:
        # CORREÇÃO: cache evita re-scan do disco a cada requisição.
        # Passe refresh=True para forçar re-leitura após adicionar arquivos.
        if self._structure_cache is not None and not refresh:
            return self._structure_cache

        structure: dict = {}
        for root, dirs, files in os.walk(self.media_dir):
            dirs.sort()
            relative_root = os.path.relpath(root, self.media_dir)

            if relative_root == ".":
                continue

            parts = relative_root.split(os.sep)

            if len(parts) == 1:
                structure.setdefault(parts[0], {})

            elif len(parts) == 2:
                series, season = parts
                structure.setdefault(series, {})
                structure[series].setdefault(season, [])

                for file in files:
                    if file.lower().endswith(self.SUPPORTED_EXTENSIONS):
                        full_path = os.path.join(root, file)
                        # CORREÇÃO: remove extensão para qualquer formato suportado,
                        # não apenas .mp4.
                        name = file
                        for ext in self.SUPPORTED_EXTENSIONS:
                            if file.lower().endswith(ext):
                                name = file[: -len(ext)]
                                break
                        structure[series][season].append({
                            "name": name,
                            "path": full_path,
                        })

        self._structure_cache = structure
        return structure

    def invalidate_cache(self):
        self._structure_cache = None

    def get_next_episode(self, path: str) -> str | None:
        """Próximo episódio após `path`: o próximo na mesma temporada; se for o
        último, o primeiro episódio da próxima temporada. None se for o último
        episódio da série. Ordenação igual à exibida na UI (sorted por nome)."""
        target = os.path.normcase(os.path.normpath(path))
        structure = self.get_structure()
        for series, seasons in structure.items():
            season_names = sorted(seasons.keys())
            for si, season in enumerate(season_names):
                eps = sorted(seasons[season], key=lambda x: x["name"])
                for ei, ep in enumerate(eps):
                    if os.path.normcase(os.path.normpath(ep["path"])) == target:
                        if ei + 1 < len(eps):
                            return eps[ei + 1]["path"]
                        for next_season in season_names[si + 1:]:
                            next_eps = sorted(seasons[next_season], key=lambda x: x["name"])
                            if next_eps:
                                return next_eps[0]["path"]
                        return None
        return None

    @staticmethod
    def get_series_library(series_dir: str) -> "MediaLibrary":
        return MediaLibrary(series_dir)

    @staticmethod
    def get_movies_library(movies_dir: str) -> "MediaLibrary":
        return MediaLibrary(movies_dir)


if __name__ == "__main__":
    from streaming.config import ConfigManager

    config = ConfigManager()
    library = MediaLibrary(config.media_dir)

    for v in library.list_videos():
        print(v)
