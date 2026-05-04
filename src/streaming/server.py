from urllib import request

from aiohttp import web
from streaming.config import ConfigManager
from streaming.media import MediaLibrary
import jinja2
import aiohttp_jinja2
import os


class StreamingServer:
    def __init__(self):
        self.config = ConfigManager()
        self.library = MediaLibrary(self.config.media_dir)
        self.app = web.Application()

        self._setup_routes()
        aiohttp_jinja2.setup(
            self.app,
            loader=jinja2.FileSystemLoader("templates")
        )

    def _setup_routes(self):
        self.app.router.add_get("/", self.handle_index)
        self.app.router.add_get("/video", self.handle_video)
        self.app.router.add_get("/watch", self.handle_watch)
        self.app.router.add_get("/series", self.handle_series)
        self.app.router.add_get("/season", self.handle_season)

    @aiohttp_jinja2.template("index.html")
    async def handle_index(self, request):
        structure = self.library.get_structure()
        series_list = list(structure.keys())

        return {"series": series_list}
    
    @aiohttp_jinja2.template("series.html")
    async def handle_series(self, request):
        series_name = request.query.get("name")

        if not series_name:
            return web.Response(text="Série não especificada", status=400)

        structure = self.library.get_structure()
        seasons = structure.get(series_name, {})

        return {
            "series": series_name,
            "seasons": sorted(seasons.keys())
        }
    
    @aiohttp_jinja2.template("season.html")
    async def handle_season(self, request):
        series_name = request.query.get("series")
        season_name = request.query.get("season")

        if not series_name or not season_name:
            return web.Response(text="Parâmetros inválidos", status=400)

        structure = self.library.get_structure()

        episodes = sorted(
            structure.get(series_name, {}).get(season_name, []),
            key=lambda x: x["name"]
        )

        return {
            "series": series_name,
            "season": season_name,
            "episodes": episodes
        }

    @aiohttp_jinja2.template("player.html")
    async def handle_watch(self, request):
        path = request.query.get("path")
        return {"path": path}

    async def handle_video(self, request):
        file_path = request.query.get("path")

        if not file_path:
            return web.Response(text="Arquivo não especificado", status=400)

        # 🔒 segurança
        if not os.path.abspath(file_path).startswith(
            os.path.abspath(self.config.media_dir)
        ):
            return web.Response(text="Acesso negado", status=403)
        
        if not os.path.isfile(file_path):
            return web.Response(text="Arquivo inválido", status=404)
        
        file_size = os.path.getsize(file_path)
        range_header = request.headers.get("Range", None)

        headers = {
            "Accept-Ranges": "bytes",
            "Content-Type": "video/mp4"
        }

        if range_header:
            start, end = range_header.replace("bytes=", "").split("-")
            start = int(start)
            end = int(end) if end else file_size - 1
            
            if start >= file_size:
                return web.Response(status=416)

            length = end - start + 1

            headers.update({
                "Content-Range": f"bytes {start}-{end}/{file_size}",
                "Content-Length": str(length),
            })

            with open(file_path, "rb") as f:
                f.seek(start)
                chunk = f.read(length)

            return web.Response(
                status=206,
                body=chunk,
                headers=headers
            )


        # fallback (arquivo inteiro)
        return web.FileResponse(path=file_path)

    def run(self):
        web.run_app(self.app, host=self.config.host, port=self.config.port)


def main():
    server = StreamingServer()
    server.run()


if __name__ == "__main__":
    main()