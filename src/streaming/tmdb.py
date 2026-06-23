import aiohttp
from streaming.database import get_metadata, upsert_metadata

TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w300"
TMDB_API_BASE = "https://api.themoviedb.org/3"


async def _search(token: str, endpoint: str, query: str) -> dict | None:
    headers = {"Authorization": f"Bearer {token}", "accept": "application/json"}
    params = {"query": query, "language": "pt-BR", "page": 1}
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{TMDB_API_BASE}/{endpoint}", headers=headers, params=params) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            results = data.get("results", [])
            return results[0] if results else None


async def fetch_metadata(token: str, name: str, media_type: str = "tv") -> dict:
    """Retorna metadata do cache ou busca no TMDB. media_type: 'tv' ou 'movie'."""
    cached = await get_metadata(name)
    if cached is not None:
        return cached

    endpoint = "search/tv" if media_type == "tv" else "search/movie"
    result = await _search(token, endpoint, name)

    if result:
        poster_path = result.get("poster_path")
        poster_url = f"{TMDB_IMAGE_BASE}{poster_path}" if poster_path else None
        overview = result.get("overview") or None
        tmdb_id = result.get("id")
    else:
        poster_url = None
        overview = None
        tmdb_id = None

    await upsert_metadata(name, tmdb_id, poster_url, overview)
    return {"tmdb_id": tmdb_id, "poster_url": poster_url, "overview": overview}
