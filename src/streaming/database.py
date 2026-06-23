import aiosqlite
import pathlib

DB_PATH = pathlib.Path(__file__).resolve().parent.parent.parent / "streaming.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS profiles (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);
"""

_SEED = [("Pedro",), ("Francieli",)]


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(_SCHEMA)
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


async def get_profile(profile_id: int) -> dict | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT id, name FROM profiles WHERE id = ?", (profile_id,)
        ) as cur:
            row = await cur.fetchone()
    return dict(row) if row else None
