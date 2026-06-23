import aiosqlite
import pathlib

DB_PATH = pathlib.Path(__file__).resolve().parent.parent.parent / "streaming.db"

_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS profiles (
        id   INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS media_metadata (
        media_key   TEXT PRIMARY KEY,
        tmdb_id     INTEGER,
        poster_url  TEXT,
        overview    TEXT,
        fetched_at  TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS watch_progress (
        profile_id  INTEGER NOT NULL,
        file_path   TEXT NOT NULL,
        position    REAL NOT NULL,
        duration    REAL,
        updated_at  TEXT NOT NULL,
        PRIMARY KEY (profile_id, file_path),
        FOREIGN KEY (profile_id) REFERENCES profiles(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS ratings (
        profile_id  INTEGER NOT NULL,
        media_key   TEXT NOT NULL,
        rating      TEXT NOT NULL,
        updated_at  TEXT NOT NULL,
        PRIMARY KEY (profile_id, media_key),
        FOREIGN KEY (profile_id) REFERENCES profiles(id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS watchlist (
        profile_id  INTEGER NOT NULL,
        media_key   TEXT NOT NULL,
        title       TEXT NOT NULL,
        poster_url  TEXT,
        media_type  TEXT NOT NULL,
        link_url    TEXT NOT NULL,
        added_at    TEXT NOT NULL,
        PRIMARY KEY (profile_id, media_key),
        FOREIGN KEY (profile_id) REFERENCES profiles(id)
    )
    """,
]

_SEED = [("Pedro",), ("Francieli",)]


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        for stmt in _STATEMENTS:
            await db.execute(stmt)
        await db.commit()
        for (name,) in _SEED:
            await db.execute(
                "INSERT OR IGNORE INTO profiles (name) VALUES (?)", (name,)
            )
        await db.commit()


async def get_all_profiles() -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT id, name FROM profiles ORDER BY id") as cur:
            rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def upsert_progress(profile_id: int, file_path: str, position: float, duration: float | None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO watch_progress (profile_id, file_path, position, duration, updated_at)
            VALUES (?, ?, ?, ?, datetime('now'))
            ON CONFLICT(profile_id, file_path) DO UPDATE SET
                position   = excluded.position,
                duration   = excluded.duration,
                updated_at = excluded.updated_at
            """,
            (profile_id, file_path, position, duration),
        )
        await db.commit()


async def get_progress(profile_id: int, file_path: str) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT position, duration FROM watch_progress WHERE profile_id = ? AND file_path = ?",
            (profile_id, file_path),
        ) as cur:
            row = await cur.fetchone()
    return dict(row) if row else None


async def get_metadata(media_key: str) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT tmdb_id, poster_url, overview FROM media_metadata WHERE media_key = ?",
            (media_key,),
        ) as cur:
            row = await cur.fetchone()
    return dict(row) if row else None


async def upsert_metadata(media_key: str, tmdb_id: int | None, poster_url: str | None, overview: str | None):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO media_metadata (media_key, tmdb_id, poster_url, overview, fetched_at)
            VALUES (?, ?, ?, ?, datetime('now'))
            ON CONFLICT(media_key) DO UPDATE SET
                tmdb_id    = excluded.tmdb_id,
                poster_url = excluded.poster_url,
                overview   = excluded.overview,
                fetched_at = excluded.fetched_at
            """,
            (media_key, tmdb_id, poster_url, overview),
        )
        await db.commit()


async def delete_progress(profile_id: int, file_path: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM watch_progress WHERE profile_id = ? AND file_path = ?",
            (profile_id, file_path),
        )
        await db.commit()


async def get_in_progress(profile_id: int) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """
            SELECT file_path, position, duration
            FROM watch_progress
            WHERE profile_id = ?
              AND position > 5
              AND duration IS NOT NULL
              AND (duration - position) > 30
            ORDER BY updated_at DESC
            """,
            (profile_id,),
        ) as cur:
            rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def upsert_rating(profile_id: int, media_key: str, rating: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO ratings (profile_id, media_key, rating, updated_at)
            VALUES (?, ?, ?, datetime('now'))
            ON CONFLICT(profile_id, media_key) DO UPDATE SET
                rating     = excluded.rating,
                updated_at = excluded.updated_at
            """,
            (profile_id, media_key, rating),
        )
        await db.commit()


async def get_rating(profile_id: int, media_key: str) -> str | None:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT rating FROM ratings WHERE profile_id = ? AND media_key = ?",
            (profile_id, media_key),
        ) as cur:
            row = await cur.fetchone()
    return row[0] if row else None


async def add_to_watchlist(profile_id: int, media_key: str, title: str, poster_url: str | None, media_type: str, link_url: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """
            INSERT INTO watchlist (profile_id, media_key, title, poster_url, media_type, link_url, added_at)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            ON CONFLICT(profile_id, media_key) DO NOTHING
            """,
            (profile_id, media_key, title, poster_url, media_type, link_url),
        )
        await db.commit()


async def remove_from_watchlist(profile_id: int, media_key: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "DELETE FROM watchlist WHERE profile_id = ? AND media_key = ?",
            (profile_id, media_key),
        )
        await db.commit()


async def get_watchlist(profile_id: int) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT media_key, title, poster_url, media_type, link_url FROM watchlist WHERE profile_id = ? ORDER BY added_at DESC",
            (profile_id,),
        ) as cur:
            rows = await cur.fetchall()
    return [dict(r) for r in rows]


async def get_watchlist_keys(profile_id: int) -> set[str]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT media_key FROM watchlist WHERE profile_id = ?",
            (profile_id,),
        ) as cur:
            rows = await cur.fetchall()
    return {r[0] for r in rows}


async def get_profile(profile_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT id, name FROM profiles WHERE id = ?", (profile_id,)
        ) as cur:
            row = await cur.fetchone()
    return dict(row) if row else None
