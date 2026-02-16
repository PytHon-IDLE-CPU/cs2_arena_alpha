# bot.py
import asyncio
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from config import API_TOKEN, ADMIN_ID, CASE_COST, SKINS
from database import init_db, get_user, update_user_field, add_skin, add_suggestion, get_skins
from keyboards import main_menu_kb, open_case_kb
from game_logic import restore_energy_loop, simulate_match

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# ----------------------------
# Старт
# ----------------------------
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Добро пожаловать в CS2 Arena Manager!", reply_markup=main_menu_kb())

# ----------------------------
# Идеи игроков
# ----------------------------
user_suggestion_waiting = set()

# Обработка нажатия на "Моя Команда"
@dp.message(F.text == "Моя Команда 👨‍🏫")
async def cmd_my_team(message: types.Message):
    await message.answer(
        "<b>🏠 Управление командой</b>\nЗдесь вы можете настроить состав, тактику и финансы.",
        reply_markup=my_team_kb()
    )

# Обработка нажатия на "Трансферный Рынок"
@dp.message(F.text == "Трансферный Рынок 📈")
async def cmd_market(message: types.Message):
    await message.answer(
        "<b>⚖️ Трансферный рынок</b>\nПокупайте таланты или продавайте своих игроков.",
        reply_markup=market_kb()
    )

# Пример обработки Inline-кнопки "Список Игроков"
@dp.callback_query(F.data == "team_players")
async def show_players(call: types.CallbackQuery):
    # Тут должна быть логика получения игроков из БД
    # Пока для примера:
    sample_players = [(1, "ShadowStrike"), (2, "Pryanichek")]
    await call.message.edit_text(
        "<b>👥 Список ваших игроков:</b>",
        reply_markup=players_list_kb(sample_players)
    )

# ----------------------------
# Открытие кейса
# ----------------------------
@dp.callback_query(F.data == "open_case")
async def open_case(call: types.CallbackQuery):
    user_id = call.from_user.id
    user = await get_user(user_id)
    coins = user[1]
    if coins < CASE_COST:
        await call.message.answer("Недостаточно монет для открытия кейса!")
        return
    await update_user_field(user_id, "coins", coins - CASE_COST)
    await call.message.edit_text("📦 Распаковка...")
    await asyncio.sleep(1)
    await call.message.edit_text("⏳ Крутим барабан...")
    await asyncio.sleep(1)
    skin = random.choice(SKINS)
    await add_skin(user_id, skin[0], skin[1], skin[2])
    await call.message.edit_text(f"✨ Выпал {skin[0]} ({skin[1]})! +{skin[2]} к Aim!")

# ----------------------------
# Запуск бота
# ----------------------------
async def main():
    await init_db()
    asyncio.create_task(restore_energy_loop())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

