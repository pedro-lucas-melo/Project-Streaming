from aiohttp import web
from streaming.config import ConfigManager
from streaming.media import MediaLibrary
import jinja2
import aiohttp_jinja2
import os
import pathlib

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent


class StreamingServer:
    def __init__(self):
        self.config = ConfigManager()
        self.series_library = MediaLibrary(self.config.media_series_dir) if self.config.media_series_dir else None
        self.movies_library = MediaLibrary(self.config.media_movies_dir) if self.config.media_movies_dir else None
        self.app = web.Application()

        self._setup_routes()
        # CORREÇÃO: autoescape=True evita XSS em qualquer variável de template.
        # CORREÇÃO: path absoluto evita quebrar quando o CWD não é streaming-server/.
        aiohttp_jinja2.setup(
            self.app,
            loader=jinja2.FileSystemLoader(str(BASE_DIR / "templates")),
            app_key=aiohttp_jinja2.APP_KEY,
            autoescape=jinja2.select_autoescape(["html"]),
        )

    def _setup_routes(self):
        self.app.router.add_get("/", self.handle_home)
        self.app.router.add_get("/series-list", self.handle_index)
        self.app.router.add_get("/video", self.handle_video)
        self.app.router.add_get("/watch", self.handle_watch)
        self.app.router.add_get("/series", self.handle_series)
        self.app.router.add_get("/season", self.handle_season)
        self.app.router.add_get("/movies", self.handle_movies)

    @aiohttp_jinja2.template("home.html")
    async def handle_home(self, request):
        return {}

    @aiohttp_jinja2.template("index.html")
    async def handle_index(self, request):
        if not self.series_library:
            raise web.HTTPNotFound(reason="Diretório de séries não configurado")
        structure = self.series_library.get_structure()
        return {"series": sorted(structure.keys())}

    @aiohttp_jinja2.template("movies.html")
    async def handle_movies(self, request):
        if not self.movies_library:
            raise web.HTTPNotFound(reason="Diretório de filmes não configurado")
        videos = self.movies_library.list_videos()
        movies = sorted(
            [
                {
                    "name": v["name"][:-4] if v["name"].lower().endswith((".mp4", ".mkv")) else v["name"],
                    "path": v["path"],
                }
                for v in videos
            ],
            key=lambda x: x["name"],
        )
        return {"movies": movies}

    @aiohttp_jinja2.template("series.html")
    async def handle_series(self, request):
        series_name = request.query.get("name")
        if not series_name:
            raise web.HTTPBadRequest(reason="Série não especificada")
        if not self.series_library:
            raise web.HTTPNotFound(reason="Diretório de séries não configurado")
        structure = self.series_library.get_structure()
        seasons = structure.get(series_name, {})
        return {"series": series_name, "seasons": sorted(seasons.keys())}

    @aiohttp_jinja2.template("season.html")
    async def handle_season(self, request):
        series_name = request.query.get("series")
        season_name = request.query.get("season")
        if not series_name or not season_name:
            raise web.HTTPBadRequest(reason="Parâmetros inválidos")
        if not self.series_library:
            raise web.HTTPNotFound(reason="Diretório de séries não configurado")
        structure = self.series_library.get_structure()
        episodes = sorted(
            structure.get(series_name, {}).get(season_name, []),
            key=lambda x: x["name"],
        )
        return {"series": series_name, "season": season_name, "episodes": episodes}

    @aiohttp_jinja2.template("player.html")
    async def handle_watch(self, request):
        path = request.query.get("path")
        if not path:
            raise web.HTTPBadRequest(reason="Caminho não especificado")
        return {"path": path}

    async def handle_video(self, request):
        file_path = request.query.get("path")
        if not file_path:
            return web.Response(text="Arquivo não especificado", status=400)

        allowed_paths = []
        if self.config.media_series_dir:
            allowed_paths.append(os.path.abspath(self.config.media_series_dir).lower())
        if self.config.media_movies_dir:
            allowed_paths.append(os.path.abspath(self.config.media_movies_dir).lower())

        # CORREÇÃO: comparação case-insensitive para Windows (NTFS não diferencia maiúsculas)
        abs_file = os.path.abspath(file_path).lower()
        if not any(abs_file.startswith(p) for p in allowed_paths):
            return web.Response(text="Acesso negado", status=403)

        if not os.path.isfile(file_path):
            return web.Response(text="Arquivo não encontrado", status=404)

        file_size = os.path.getsize(file_path)
        range_header = request.headers.get("Range")

        ext = os.path.splitext(file_path)[1].lower()
        content_type = "video/mp4" if ext == ".mp4" else "video/x-matroska"

        headers = {
            "Accept-Ranges": "bytes",
            "Content-Type": content_type,
        }

        if range_header:
            range_val = range_header.replace("bytes=", "")
            start_str, _, end_str = range_val.partition("-")
            start = int(start_str) if start_str else 0
            end = int(end_str) if end_str else file_size - 1

            if start >= file_size:
                return web.Response(status=416)

            end = min(end, file_size - 1)
            length = end - start + 1
            headers.update({
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Content-Length": str(length),
            })

            # CORREÇÃO: StreamResponse em vez de ler tudo na memória de uma vez.
            # Evita consumir GB de RAM para ranges grandes.
            response = web.StreamResponse(status=206, headers=headers)
            await response.prepare(request)

            CHUNK = 256 * 1024  # 256 KB por vez
            remaining = length
            try:
                with open(file_path, "rb") as f:
                    f.seek(start)
                    while remaining > 0:
                        data = f.read(min(CHUNK, remaining))
                        if not data:
                            break
                        await response.write(data)
                        remaining -= len(data)
                await response.write_eof()
            except ConnectionError:
                pass  # cliente fechou conexão (seek, pause, tab fechada) — comportamento normal
            return response

        return web.FileResponse(path=file_path, headers={"Content-Type": content_type})

    def run(self):
        web.run_app(self.app, host=self.config.host, port=self.config.port)


def main():
    server = StreamingServer()
    server.run()


if __name__ == "__main__":
    main()
