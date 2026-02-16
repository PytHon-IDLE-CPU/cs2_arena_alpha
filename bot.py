# bot.py
import asyncio
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from config import BOT_TOKEN, ADMIN_ID, CASE_COST, SKINS
from database import init_db, get_user, update_user_balance, add_player, get_team_players
from keyboards import main_menu_kb, open_case_kb
from game_logic import restore_energy_loop, simulate_match

Bot(token=BOT_TOKEN)
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

@dp.message()
async def handle_suggestions(message: types.Message):
    if message.text == "💡 Предложить идею":
        await message.answer("Напиши свою идею, я передам её администрации.")
        user_suggestion_waiting.add(message.from_user.id)
    elif message.from_user.id in user_suggestion_waiting:
        await add_suggestion(message.from_user.id, message.text)
        await bot.send_message(ADMIN_ID, f"Новая идея от {message.from_user.id}: {message.text}")
        await message.answer("Спасибо! Твоя идея отправлена администрации.")
        user_suggestion_waiting.remove(message.from_user.id)

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
    await update_user_balance(user_id, "coins", coins - CASE_COST)
    await call.message.edit_text("📦 Распаковка...")
    await asyncio.sleep(1)
    await call.message.edit_text("⏳ Крутим барабан...")
    await asyncio.sleep(1)
    skin = random.choice(SKINS)
    await add_player(user_id, skin[0], skin[1], skin[2])
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


