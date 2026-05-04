from aiohttp import web
from streaming.config import ConfigManager
from streaming.media import MediaLibrary


class StreamingServer:
    def __init__(self):
        self.config = ConfigManager()
        self.library = MediaLibrary(self.config.media_dir)
        self.app = web.Application()

        self._setup_routes()

    def _setup_routes(self):
        self.app.router.add_get("/", self.handle_index)
        self.app.router.add_get("/video", self.handle_video)

    async def handle_index(self, request):
        videos = self.library.list_videos()

        response_text = "<h1>Lista de Vídeos</h1><ul>"

        for video in videos:
            response_text += (
                f"<li>"
                f"<a href='/video?path={video['path']}'>"
                f"{video['relative_path']}"
                f"</a>"
                f"</li>"
            )

        response_text += "</ul>"

        return web.Response(text=response_text, content_type="text/html")
    
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