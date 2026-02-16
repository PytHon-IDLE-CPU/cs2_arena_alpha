# database.py
import aiosqlite
from config import DB_PATH

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            coins INTEGER DEFAULT 10000,
            morale INTEGER DEFAULT 50,
            team_spirit INTEGER DEFAULT 50,
            fans_count INTEGER DEFAULT 0,
            last_train_time TEXT,
            ace_bet_active INTEGER DEFAULT 0
        )""")
        await db.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            rarity TEXT,
            aim INTEGER,
            reaction INTEGER,
            tactics INTEGER,
            synergy INTEGER,
            clutch INTEGER,
            perk TEXT,
            energy INTEGER DEFAULT 100,
            injured_until TEXT
        )""")
        await db.execute("""
        CREATE TABLE IF NOT EXISTS skins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            rarity TEXT,
            aim_bonus INTEGER
        )""")
        await db.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            case_type TEXT
        )""")
        await db.execute("""
        CREATE TABLE IF NOT EXISTS suggestions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            text TEXT,
            timestamp TEXT
        )""")
        await db.commit()


# ----------------------------
# Функции для юзеров
# ----------------------------
async def get_user(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cur:
            row = await cur.fetchone()
            if not row:
                await db.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
                await db.commit()
                return await get_user(user_id)
            return row

async def update_user_field(user_id: int, field: str, value):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(f"UPDATE users SET {field} = ? WHERE user_id = ?", (value, user_id))
        await db.commit()

async def add_skin(user_id: int, name: str, rarity: str, aim_bonus: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO skins (user_id, name, rarity, aim_bonus) VALUES (?,?,?,?)",
            (user_id, name, rarity, aim_bonus)
        )
        await db.commit()

async def get_skins(user_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute("SELECT * FROM skins WHERE user_id = ?", (user_id,)) as cur:
            return await cur.fetchall()

async def add_suggestion(user_id: int, text: str):
    import datetime
    ts = datetime.datetime.now().isoformat()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO suggestions (user_id, text, timestamp) VALUES (?,?,?)",
            (user_id, text, ts)
        )
        await db.commit()
