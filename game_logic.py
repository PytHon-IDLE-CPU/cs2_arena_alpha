# game_logic.py
import asyncio
import random
from database import get_user, get_skins, update_user_field
from config import MATCH_EVENTS, MAPS, ENERGY_RESTORE_INTERVAL, ENERGY_RESTORE_AMOUNT, SKINS

# ----------------------------
# Дивизионы
# ----------------------------
DIVISIONS = [
    ("Подвальные Воины", "Даже в подвале рождаются чемпионы — поднимайся, пока другие спят!"),
    ("Мастера Компьютерных Клубов", "Ты уже не новичок, но твой потенциал — за пределами этих клубов. Время идти выше!"),
    ("Региональные Ассы", "Локальная слава — только начало. Покажи, что твой талант не знает границ!"),
    ("Национальные Звёзды", "Ты уже на вершине страны, но настоящая легенда рождается там, где боятся подняться!"),
    ("Бессмертные Легенды", "Ты вошёл в историю. Но даже легенды продолжают писать свои эпопеи — не останавливайся!")
]

def get_division(fans_count: int):
    thresholds = [0, 500, 2000, 5000, 10000]
    for i, t in enumerate(thresholds[::-1]):
        if fans_count >= t:
            return DIVISIONS[len(thresholds)-1-i]
    return DIVISIONS[0]

# ----------------------------
# Восстановление энергии
# ----------------------------
async def restore_energy_loop():
    while True:
        await asyncio.sleep(ENERGY_RESTORE_INTERVAL)
        async with aiosqlite.connect("cs2_arena.db") as db:
            await db.execute("UPDATE players SET energy = MIN(100, energy + ?)", (ENERGY_RESTORE_AMOUNT,))
            await db.commit()

# ----------------------------
# Симуляция матча
# ----------------------------
async def simulate_match(user_id: int, send_func):
    user = await get_user(user_id)
    # Проверка энергии игроков
    import aiosqlite
    async with aiosqlite.connect("cs2_arena.db") as db:
        async with db.execute("SELECT energy FROM players WHERE user_id=?", (user_id,)) as cur:
            energies = await cur.fetchall()
        avg_energy = sum([e[0] for e in energies]) / max(1, len(energies))
        if avg_energy < 20:
            await send_func("Твои бойцы слишком устали, отправь их отдыхать или на тренировку!")
            return

    # Сумма бонусов скинов
    skins = await get_skins(user_id)
    aim_bonus = sum([skin[3] for skin in skins])

    # Матч
    score_a, score_b = 0, 0
    map_name = random.choice(MAPS)
    message = await send_func(f"Матч начался на карте {map_name}! Счет 0-0")
    for round_num in range(1, 14):
        event = random.choice(MATCH_EVENTS)
        score_a += 1  # Для простоты, игрок выигрывает раунд
        await message.edit_text(f"Раунд {round_num}: {event} | Счет: {score_a}-{score_b}")
        await asyncio.sleep(1)
        if score_a >= 13:
            await message.edit_text(f"Матч окончен! Победили игроки {user_id}!")
            break
