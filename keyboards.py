# keyboards.py
from aiogram.types import InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from config import TRAINING_OPTIONS

def main_menu_kb():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton("💡 Предложить идею"))
    builder.add(KeyboardButton("Мой состав"), KeyboardButton("Тренировка"))
    builder.add(KeyboardButton("Играть матч"), KeyboardButton("Статус команды"))
    return builder.as_markup(resize_keyboard=True)

def training_kb():
    builder = InlineKeyboardBuilder()
    for name, _, _, _, _, _ in TRAINING_OPTIONS:
        builder.add(InlineKeyboardButton(text=name, callback_data=f"train_{name}"))
    return builder.as_markup()

def ace_bet_kb():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton("Ставлю!", callback_data="bet_yes"))
    builder.add(InlineKeyboardButton("Пропустить", callback_data="bet_no"))
    return builder.as_markup()

def open_case_kb():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton("Открыть кейс", callback_data="open_case"))
    return builder.as_markup()
