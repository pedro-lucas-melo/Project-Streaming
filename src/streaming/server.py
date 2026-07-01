from aiohttp import web
from streaming.config import ConfigManager
from streaming.media import MediaLibrary
from streaming.database import (
    init_db, get_all_profiles, get_profile,
    upsert_progress, get_progress, get_in_progress, delete_progress,
    upsert_rating, get_rating,
    add_to_watchlist, remove_from_watchlist, get_watchlist, get_watchlist_keys,
)
from streaming.tmdb import fetch_metadata, search_suggestions
import asyncio
import jinja2
import aiohttp_jinja2
import os
import re
import pathlib
from urllib.parse import quote

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
        self.app.router.add_get("/", self.handle_profiles)
        self.app.router.add_get("/profiles", self.handle_profiles_redirect)
        self.app.router.add_post("/profiles/select", self.handle_profile_select)
        self.app.router.add_get("/profiles/exit", self.handle_profile_exit)
        self.app.router.add_get("/profile/{name}", self.handle_home)
        self.app.router.add_get("/series-list", self.handle_index)
        self.app.router.add_get("/video", self.handle_video)
        self.app.router.add_get("/watch", self.handle_watch)
        self.app.router.add_get("/series", self.handle_series)
        self.app.router.add_get("/season", self.handle_season)
        self.app.router.add_get("/movies", self.handle_movies)
        self.app.router.add_post("/api/progress", self.handle_progress_save)
        self.app.router.add_get("/api/progress", self.handle_progress_get)
        self.app.router.add_delete("/api/progress", self.handle_progress_delete)
        self.app.router.add_get("/api/tmdb-search", self.handle_tmdb_search)
        self.app.router.add_post("/api/suggest", self.handle_suggest)
        # AVALIAÇÃO DESABILITADA — remover comentário para reativar
        # self.app.router.add_get("/api/rating", self.handle_rating_get)
        # self.app.router.add_post("/api/rating", self.handle_rating_post)
        self.app.router.add_get("/api/watchlist", self.handle_watchlist_get)
        self.app.router.add_post("/api/watchlist", self.handle_watchlist_post)
        self.app.router.add_delete("/api/watchlist", self.handle_watchlist_delete)
        self.app.router.add_static("/static", BASE_DIR / "static")
        self.app.on_startup.append(self._on_startup)

    async def _on_startup(self, app):
        await init_db()

    def _require_profile(self, request: web.Request) -> int | None:
        """Retorna profile_id do cookie ou None."""
        try:
            return int(request.cookies.get("profile_id", ""))
        except (ValueError, TypeError):
            return None

    async def handle_profiles_redirect(self, request: web.Request):
        raise web.HTTPFound("/")

    @aiohttp_jinja2.template("profiles.html")
    async def handle_profiles(self, request):
        profiles = await get_all_profiles()
        return {"profiles": profiles}

    async def handle_profile_select(self, request: web.Request):
        data = await request.post()
        try:
            profile_id = int(data["profile_id"])
        except (KeyError, ValueError):
            raise web.HTTPBadRequest(reason="profile_id inválido")
        profile = await get_profile(profile_id)
        if not profile:
            raise web.HTTPNotFound(reason="Perfil não encontrado")
        name_slug = re.sub(r"[^a-z0-9]+", "-", profile["name"].lower()).strip("-")
        response = web.HTTPFound(f"/profile/{name_slug}")
        response.set_cookie("profile_id", str(profile_id))
        raise response

    async def handle_profile_exit(self, request: web.Request):
        response = web.HTTPFound("/")
        response.del_cookie("profile_id")
        raise response

    @aiohttp_jinja2.template("home.html")
    async def handle_home(self, request):
        profile_id = self._require_profile(request)
        if not profile_id:
            raise web.HTTPFound("/")
        profile = await get_profile(profile_id)
        if not profile:
            raise web.HTTPFound("/")
        in_progress = await get_in_progress(profile_id)
        series_base = os.path.abspath(self.config.media_series_dir).lower() if self.config.media_series_dir else ""
        enriched = []
        seen_series: set[str] = set()  # 1 card por série (episódio mais recente), nunca duplica
        for item in in_progress:
            fp = item["file_path"]
            abs_fp = os.path.abspath(fp).lower()
            pct = int((item["position"] / item["duration"]) * 100)
            encoded_path = quote(fp)
            if series_base and abs_fp.startswith(series_base):
                parts = pathlib.Path(fp).parts
                # estrutura: .../series/SeriesName/Season/Episode.mp4
                series_idx = next((i for i, p in enumerate(parts) if p.lower() == pathlib.Path(self.config.media_series_dir).name.lower()), None)
                if series_idx is not None and len(parts) > series_idx + 2:
                    series_name = parts[series_idx + 1]
                    episode_name = pathlib.Path(fp).stem
                else:
                    series_name = pathlib.Path(fp).stem
                    episode_name = None
                # in_progress vem ordenado por updated_at DESC → 1ª ocorrência = mais recente
                if series_name in seen_series:
                    continue
                seen_series.add(series_name)
                meta = await fetch_metadata(self.config.tmdb_token, series_name, "tv")
                enriched.append({
                    "type": "series",
                    "title": series_name,
                    "subtitle": episode_name,
                    "poster_url": meta.get("poster_url"),
                    "pct": pct,
                    "encoded_path": encoded_path,
                    "file_path": fp,
                })
            else:
                movie_name = pathlib.Path(fp).stem
                for ext in (".mp4", ".mkv"):
                    if movie_name.lower().endswith(ext):
                        movie_name = movie_name[:-len(ext)]
                meta = await fetch_metadata(self.config.tmdb_token, movie_name, "movie")
                enriched.append({
                    "type": "movie",
                    "title": movie_name,
                    "subtitle": None,
                    "poster_url": meta.get("poster_url"),
                    "pct": pct,
                    "encoded_path": encoded_path,
                    "file_path": fp,
                })
        watchlist = await get_watchlist(profile_id)
        return {"profile": profile, "in_progress": enriched, "watchlist": watchlist}

    def _profile_slug(self, profile: dict | None) -> str:
        if not profile:
            return ""
        return re.sub(r"[^a-z0-9]+", "-", profile["name"].lower()).strip("-")

    @aiohttp_jinja2.template("index.html")
    async def handle_index(self, request):
        if not self.series_library:
            raise web.HTTPNotFound(reason="Diretório de séries não configurado")
        profile_id = self._require_profile(request)
        profile = await get_profile(profile_id) if profile_id else None
        wl_keys = await get_watchlist_keys(profile_id) if profile_id else set()
        structure = self.series_library.get_structure()
        series_names = sorted(structure.keys())
        series = []
        for name in series_names:
            meta = await fetch_metadata(self.config.tmdb_token, name, "tv")
            series.append({"name": name, "poster_url": meta.get("poster_url"), "in_watchlist": name in wl_keys, "encoded_name": quote(name)})
        return {"series": series, "profile_slug": self._profile_slug(profile)}

    @aiohttp_jinja2.template("movies.html")
    async def handle_movies(self, request):
        if not self.movies_library:
            raise web.HTTPNotFound(reason="Diretório de filmes não configurado")
        profile_id = self._require_profile(request)
        profile = await get_profile(profile_id) if profile_id else None
        wl_keys = await get_watchlist_keys(profile_id) if profile_id else set()
        videos = self.movies_library.list_videos()
        movies_raw = sorted(
            [
                {
                    "name": v["name"][:-4] if v["name"].lower().endswith((".mp4", ".mkv")) else v["name"],
                    "path": v["path"],
                }
                for v in videos
            ],
            key=lambda x: x["name"],
        )
        movies = []
        for m in movies_raw:
            meta = await fetch_metadata(self.config.tmdb_token, m["name"], "movie")
            movies.append({**m, "poster_url": meta.get("poster_url"), "in_watchlist": m["name"] in wl_keys, "encoded_path": quote(m["path"])})
        return {"movies": movies, "profile_slug": self._profile_slug(profile)}

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

    @staticmethod
    def _strip_media_ext(filename: str) -> str:
        # Remove só a extensão real do fim (.mp4/.mkv), preservando extensões
        # "artísticas" que fazem parte do nome (ex.: Mr Robot "hellofriend.mov",
        # "da3m0ns.mp4"). Mesma lógica da listagem em MediaLibrary.get_structure.
        for ext in MediaLibrary.SUPPORTED_EXTENSIONS:
            if filename.lower().endswith(ext):
                return filename[: -len(ext)]
        return filename

    @aiohttp_jinja2.template("player.html")
    async def handle_watch(self, request):
        path = request.query.get("path")
        if not path:
            raise web.HTTPBadRequest(reason="Caminho não especificado")
        profile_id = self._require_profile(request)
        series_base = os.path.abspath(self.config.media_series_dir).lower() if self.config.media_series_dir else ""
        abs_path = os.path.abspath(path).lower()
        if series_base and abs_path.startswith(series_base):
            parts = pathlib.Path(path).parts
            series_idx = next((i for i, p in enumerate(parts) if p.lower() == pathlib.Path(self.config.media_series_dir).name.lower()), None)
            media_key = parts[series_idx + 1] if series_idx is not None and len(parts) > series_idx + 1 else pathlib.Path(path).stem
            media_type = "tv"
            season = parts[series_idx + 2] if series_idx is not None and len(parts) > series_idx + 2 else ""
            episode_name = self._strip_media_ext(pathlib.Path(path).name)
            display_title = " / ".join(x for x in [media_key, season, episode_name] if x)
        else:
            media_key = pathlib.Path(path).stem
            media_type = "movie"
            display_title = media_key
        current_rating = await get_rating(profile_id, media_key) if profile_id else None
        progress = await get_progress(profile_id, path) if profile_id else None
        resume_position = progress["position"] if progress and progress.get("position") else 0
        # Próximo episódio (só séries) — usado para auto-avanço ao terminar.
        next_path = None
        if media_type == "tv" and self.series_library:
            next_path = self.series_library.get_next_episode(path)
        return {
            "path": path,
            "encoded_path": quote(path),
            "media_key": media_key,
            "media_type": media_type,
            "current_rating": current_rating or "",
            "resume_position": resume_position,
            "next_encoded_path": quote(next_path) if next_path else "",
            "display_title": display_title,
        }

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
            except (ConnectionError, asyncio.CancelledError):
                pass  # cliente fechou conexão ou server shutdown
            return response

        return web.FileResponse(path=file_path, headers={"Content-Type": content_type})

    async def handle_suggest(self, request: web.Request):
        try:
            data = await request.json()
            title = data["title"]
            media_type = data.get("media_type", "")
            year = data.get("year", "")
            tmdb_url = data.get("tmdb_url", "")
        except (KeyError, TypeError, ValueError):
            return web.json_response({"error": "Dados inválidos"}, status=400)

        cfg = self.config
        if not cfg.telegram_bot_token or not cfg.telegram_chat_id:
            return web.json_response({"error": "Telegram não configurado"}, status=503)

        tipo = "Filme" if media_type == "movie" else "Série"
        text = f"💡 *Sugestão de {tipo}*: {title}"
        if year:
            text += f" ({year})"
        if tmdb_url:
            text += f"\n{tmdb_url}"

        import aiohttp as _aiohttp
        telegram_url = f"https://api.telegram.org/bot{cfg.telegram_bot_token}/sendMessage"
        async with _aiohttp.ClientSession() as session:
            async with session.post(telegram_url, json={
                "chat_id": cfg.telegram_chat_id,
                "text": text,
                "parse_mode": "Markdown",
            }) as resp:
                if resp.status == 200:
                    return web.json_response({"ok": True})
                text_err = await resp.text()
                return web.json_response({"error": text_err}, status=502)

    async def handle_tmdb_search(self, request: web.Request):
        q = request.query.get("q", "").strip()
        if not q:
            return web.json_response([])
        if not self.config.tmdb_token:
            return web.json_response([])
        results = await search_suggestions(self.config.tmdb_token, q)
        return web.json_response(results)

    async def handle_rating_get(self, request: web.Request):
        profile_id = self._require_profile(request)
        if not profile_id:
            return web.json_response({"rating": None})
        media_key = request.query.get("media_key", "")
        rating = await get_rating(profile_id, media_key)
        return web.json_response({"rating": rating})

    async def handle_rating_post(self, request: web.Request):
        profile_id = self._require_profile(request)
        if not profile_id:
            return web.Response(status=401)
        try:
            data = await request.json()
            media_key = data["media_key"]
            rating = data["rating"]
            if rating not in ("love", "like", "dislike"):
                raise ValueError
        except (KeyError, ValueError, TypeError):
            return web.Response(status=400)
        await upsert_rating(profile_id, media_key, rating)
        return web.Response(status=204)

    async def handle_watchlist_get(self, request: web.Request):
        profile_id = self._require_profile(request)
        if not profile_id:
            return web.json_response({"in_watchlist": False})
        media_key = request.query.get("media_key", "")
        keys = await get_watchlist_keys(profile_id)
        return web.json_response({"in_watchlist": media_key in keys})

    async def handle_watchlist_post(self, request: web.Request):
        profile_id = self._require_profile(request)
        if not profile_id:
            return web.Response(status=401)
        try:
            data = await request.json()
            media_key = data["media_key"]
            title = data["title"]
            poster_url = data.get("poster_url")
            media_type = data["media_type"]
            link_url = data["link_url"]
        except (KeyError, TypeError):
            return web.Response(status=400)
        await add_to_watchlist(profile_id, media_key, title, poster_url, media_type, link_url)
        return web.Response(status=204)

    async def handle_watchlist_delete(self, request: web.Request):
        profile_id = self._require_profile(request)
        if not profile_id:
            return web.Response(status=401)
        media_key = request.query.get("media_key", "")
        if not media_key:
            return web.Response(status=400)
        await remove_from_watchlist(profile_id, media_key)
        return web.Response(status=204)

    async def handle_progress_delete(self, request: web.Request):
        profile_id = self._require_profile(request)
        if not profile_id:
            return web.Response(status=401)
        file_path = request.query.get("path", "")
        if not file_path:
            return web.Response(status=400)
        await delete_progress(profile_id, file_path)
        return web.Response(status=204)

    async def handle_progress_save(self, request: web.Request):
        profile_id = self._require_profile(request)
        if not profile_id:
            return web.Response(status=401)
        try:
            data = await request.json()
            file_path = data["path"]
            position = float(data["position"])
            duration = float(data["duration"]) if data.get("duration") else None
        except (KeyError, ValueError, TypeError):
            return web.Response(status=400)
        await upsert_progress(profile_id, file_path, position, duration)
        return web.Response(status=204)

    async def handle_progress_get(self, request: web.Request):
        profile_id = self._require_profile(request)
        if not profile_id:
            return web.json_response({"position": 0, "duration": None})
        file_path = request.query.get("path", "")
        progress = await get_progress(profile_id, file_path)
        if not progress:
            return web.json_response({"position": 0, "duration": None})
        return web.json_response(progress)

    def run(self):
        # ProactorEventLoop (default no Windows) — estável p/ streaming.
        # NÃO trocar por SelectorEventLoop: tem bug "_write_send assert" + WinError 10038 em writes de socket.
        def _silence_noise(loop, context):
            exc = context.get("exception")
            if isinstance(exc, (ConnectionResetError, asyncio.InvalidStateError)):
                return
            loop.default_exception_handler(context)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.set_exception_handler(_silence_noise)

        # AppRunner manual em vez de web.run_app: shutdown limpo no Ctrl+C, sem
        # o cancel de tasks que gerava o spam de InvalidStateError.
        runner = web.AppRunner(self.app)
        loop.run_until_complete(runner.setup())
        site = web.TCPSite(runner, self.config.host, self.config.port)
        loop.run_until_complete(site.start())
        print(f"Servidor em http://{self.config.host}:{self.config.port}  (Ctrl+C para sair)")
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            # Protege também a limpeza: um Ctrl+C durante o cleanup (comum) não
            # deve vazar traceback do asyncio para o terminal.
            try:
                loop.run_until_complete(runner.cleanup())
            except KeyboardInterrupt:
                pass
            loop.close()
            print("\nServidor encerrado.")


def main():
    server = StreamingServer()
    server.run()


if __name__ == "__main__":
    main()
