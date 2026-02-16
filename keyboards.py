# keyboards.py
from aiogram.types import InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from config import TRAINING_OPTIONS

# --- Главное меню (Reply кнопки под строкой ввода) ---
def main_menu_kb():
    builder = ReplyKeyboardBuilder()
    # В aiogram 3.x используем text= для создания кнопок
    builder.row(KeyboardButton(text="💡 Предложить идею"))
    builder.row(KeyboardButton(text="Мой состав"), KeyboardButton(text="Тренировка"))
    builder.row(KeyboardButton(text="Играть матч"), KeyboardButton(text="Статус команды"))
    
    # as_markup преобразует билдер в объект клавиатуры
    return builder.as_markup(resize_keyboard=True)

# --- Меню тренировок (Inline кнопки под сообщением) ---
def training_kb():
    builder = InlineKeyboardBuilder()
    for name, _, _, _, _, _ in TRAINING_OPTIONS:
        # Для Inline кнопок всегда указываем text= и callback_data=
        builder.add(InlineKeyboardButton(text=name, callback_data=f"train_{name}"))
    
    # Делаем кнопки в один столбец
    builder.adjust(1)
    return builder.as_markup()

# --- Ставки на Эйс ---
def ace_bet_kb():
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="✅ Ставлю!", callback_data="bet_yes"),
        InlineKeyboardButton(text="❌ Пропустить", callback_data="bet_no")
    )
    return builder.as_markup()

# --- Кнопка открытия кейса ---
def open_case_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🎁 Открыть кейс (500💰)", callback_data="open_case"))
    return builder.as_markup()
