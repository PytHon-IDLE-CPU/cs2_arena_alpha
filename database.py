import aiosqlite
import json
import random
from datetime import datetime

# 1. Инициализация БД (создание таблиц)
async def init_db():
    async with aiosqlite.connect("cs2_manager.db") as db:
        # Таблица пользователей
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                balance INTEGER DEFAULT 1000,
                fans INTEGER DEFAULT 0,
                reputation INTEGER DEFAULT 50,
                team_name TEXT
            )
        ''')
        # Таблица игроков
        await db.execute('''
            CREATE TABLE IF NOT EXISTS players (
                player_id INTEGER PRIMARY KEY AUTOINCREMENT,
                owner_id INTEGER,
                nickname TEXT,
                position TEXT,
                rarity TEXT,
                aim INTEGER,
                reaction INTEGER,
                tactics INTEGER,
                stamina INTEGER DEFAULT 100,
                morale INTEGER DEFAULT 100,
                FOREIGN KEY (owner_id) REFERENCES users (user_id)
            )
        ''')
        # Таблица ставок
        await db.execute('''
            CREATE TABLE IF NOT EXISTS bets (
                bet_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount INTEGER,
                is_active BOOLEAN DEFAULT 1
            )
        ''')
        # Таблица рынка
        await db.execute('''
            CREATE TABLE IF NOT EXISTS market_players (
                user_id INTEGER PRIMARY KEY,
                data TEXT
            )
        ''')
        await db.commit()

# 2. Функции пользователя
async def create_user(user_id: int, team_name: str):
    async with aiosqlite.connect("cs2_manager.db") as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, team_name, balance) VALUES (?, ?, ?)",
            (user_id, team_name, 1000)
        )
        await db.commit()

async def get_user(user_id: int):
    async with aiosqlite.connect("cs2_manager.db") as db:
        async with db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)) as cursor:
            return await cursor.fetchone()

async def update_user_balance(user_id: int, amount: int):
    async with aiosqlite.connect("cs2_manager.db") as db:
        await db.execute("UPDATE users SET balance = balance + ? WHERE user_id = ?", (amount, user_id))
        await db.commit()

# 3. Функции игроков
async def add_player(owner_id, nickname, position, rarity):
    async with aiosqlite.connect("cs2_manager.db") as db:
        await db.execute(
            "INSERT INTO players (owner_id, nickname, position, rarity, aim, reaction, tactics, stamina, morale) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (owner_id, nickname, position, rarity, 50, 50, 50, 100, 100)
        )
        await db.commit()

async def get_team_players(owner_id: int):
    async with aiosqlite.connect("cs2_manager.db") as db:
        async with db.execute("SELECT * FROM players WHERE owner_id = ?", (owner_id,)) as cursor:
            return await cursor.fetchall()

async def get_player(player_id: int):
    async with aiosqlite.connect("cs2_manager.db") as db:
        async with db.execute("SELECT * FROM players WHERE player_id = ?", (player_id,)) as cursor:
            return await cursor.fetchone()

async def update_player_stats(player_id, **kwargs):
    async with aiosqlite.connect("cs2_manager.db") as db:
        for key, value in kwargs.items():
            if isinstance(value, str) and value.startswith('+'):
                await db.execute(f"UPDATE players SET {key} = {key} + ? WHERE player_id = ?", (int(value[1:]), player_id))
            elif isinstance(value, str) and value.startswith('-'):
                await db.execute(f"UPDATE players SET {key} = {key} - ? WHERE player_id = ?", (int(value[1:]), player_id))
            else:
                await db.execute(f"UPDATE players SET {key} = ? WHERE player_id = ?", (value, player_id))
        await db.commit()

async def reduce_player_stamina(owner_id: int, amount: int):
    async with aiosqlite.connect("cs2_manager.db") as db:
        await db.execute("UPDATE players SET stamina = MAX(0, stamina - ?) WHERE owner_id = ?", (amount, owner_id))
        await db.commit()

# 4. Рынок и ставки
async def set_market_players(user_id: int, players: list):
    data_json = json.dumps(players)
    async with aiosqlite.connect("cs2_manager.db") as db:
        await db.execute("INSERT OR REPLACE INTO market_players (user_id, data) VALUES (?, ?)", (user_id, data_json))
        await db.commit()

async def get_market_players(user_id: int):
    async with aiosqlite.connect("cs2_manager.db") as db:
        async with db.execute("SELECT data FROM market_players WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return json.loads(row[0]) if row else []

async def create_bet(user_id: int, amount: int):
    async with aiosqlite.connect("cs2_manager.db") as db:
        await db.execute("INSERT INTO bets (user_id, amount) VALUES (?, ?)", (user_id, amount))
        await db.update_user_balance(user_id, -amount) # Сразу списываем ставку
        await db.commit()

async def get_active_bet(user_id: int):
    async with aiosqlite.connect("cs2_manager.db") as db:
        async with db.execute("SELECT amount FROM bets WHERE user_id = ? AND is_active = 1", (user_id,)) as cursor:
            row = await cursor.fetchone()
            return {"amount": row[0]} if row else None

async def clear_bet(user_id: int):
    async with aiosqlite.connect("cs2_manager.db") as db:
        await db.execute("UPDATE bets SET is_active = 0 WHERE user_id = ?", (user_id,))
        await db.commit()

async def log_random_event(user_id, name, desc):
    # Заглушка для логов событий (можно расширить)
    print(f"Событие для {user_id}: {name} - {desc}")

async def add_sticker_to_collection(user_id, item, rarity):
    # Заглушка для коллекции стикеров
    pass  # <--- ОБЯЗАТЕЛЬНО ДОБАВЬ ЭТО СЛОВО С ОТСТУПОМ!

# Теперь следующая функция будет работать правильно
async def update_user_field(user_id, field, value):
    async with aiosqlite.connect("cs2_manager.db") as db:
        await db.execute(f"UPDATE users SET {field} = ? WHERE user_id = ?", (value, user_id))
        await db.commit()

async def add_skin(owner_id, nickname, position, rarity):
    await add_player(owner_id, nickname, position, rarity)

async def get_skins(owner_id):
    return await get_team_players(owner_id)

async def add_suggestion(user_id, text):
    pass # Заглушка, чтобы не было ошибки

