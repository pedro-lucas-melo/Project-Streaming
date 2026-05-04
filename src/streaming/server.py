from aiohttp import web
from streaming.config import ConfigManager
from streaming.media import MediaLibrary
import jinja2
import aiohttp_jinja2


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

    @aiohttp_jinja2.template("index.html")
    async def handle_index(self, request):
        videos = self.library.list_videos()
        return {"videos": videos}
    
    @aiohttp_jinja2.template("player.html")
    async def handle_watch(self, request):
        path = request.query.get("path")
        return {"path": path}
    
    async def handle_video(self, request):
        file_path = request.query.get("path")

        if not file_path:
            return web.Response(text="Arquivo não especificado", status=400)

        return web.FileResponse(path=file_path)
    
    

    def run(self):
        web.run_app(self.app, host=self.config.host, port=self.config.port)


def main():
    server = StreamingServer()
    server.run()


if __name__ == "__main__":
    main()