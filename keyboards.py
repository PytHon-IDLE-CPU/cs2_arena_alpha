# keyboards.py
from aiogram.types import InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

# --- 1. ГЛАВНОЕ МЕНЮ (Reply) ---
def main_menu_kb():
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="Моя Команда 👨‍🏫"), KeyboardButton(text="Трансферный Рынок 📈"))
    builder.row(KeyboardButton(text="Матчи ⚔️"), KeyboardButton(text="Турниры 🏆"))
    builder.row(KeyboardButton(text="Букмекер 💰"), KeyboardButton(text="Статистика 📊"))
    builder.row(KeyboardButton(text="Настройки ⚙️"), KeyboardButton(text="💡 Предложить идею"))
    return builder.as_markup(resize_keyboard=True, input_field_placeholder="Выберите раздел...")

# --- 2. РАЗДЕЛ "МОЯ КОМАНДА" (Inline) ---
def my_team_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Список Игроков 👥", callback_data="team_players"))
    builder.row(InlineKeyboardButton(text="Финансы 💲", callback_data="team_finance"))
    builder.row(InlineKeyboardButton(text="Тактика 🧠", callback_data="team_tactics"))
    builder.row(InlineKeyboardButton(text="Тренировки 🏋️", callback_data="team_train"))
    builder.row(InlineKeyboardButton(text="⏪ Главное Меню", callback_data="to_main"))
    builder.adjust(2, 1, 1, 1)
    return builder.as_markup()

# --- 3. СПИСОК ИГРОКОВ (Динамический Inline) ---
def players_list_kb(players):
    """
    players: список кортежей из БД [(id, name), ...]
    """
    builder = InlineKeyboardBuilder()
    for p_id, p_name in players:
        builder.add(InlineKeyboardButton(text=f"{p_name} 🏃", callback_data=f"player_profile_{p_id}"))
    
    builder.row(InlineKeyboardButton(text="Нанять Нового Игрока 🛒", callback_data="market_buy"))
    builder.row(InlineKeyboardButton(text="⏪ Назад", callback_data="back_to_team"))
    builder.adjust(2) # Игроки по 2 в ряд
    return builder.as_markup()

# --- 4. ПРОФИЛЬ ИГРОКА (Inline) ---
def player_profile_kb(player_id):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Характеристики ⭐", callback_data=f"p_stats_{player_id}"))
    builder.row(InlineKeyboardButton(text="Контракт 📜", callback_data=f"p_contract_{player_id}"))
    builder.row(InlineKeyboardButton(text="Статистика 🎯", callback_data=f"p_performance_{player_id}"))
    builder.row(InlineKeyboardButton(text="Тренировать 👨‍🏫", callback_data=f"p_train_{player_id}"))
    builder.row(InlineKeyboardButton(text="Продать Игрока 💸", callback_data=f"p_sell_{player_id}"))
    builder.row(InlineKeyboardButton(text="⏪ Назад к списку", callback_data="team_players"))
    builder.adjust(2, 1, 1, 1)
    return builder.as_markup()

# --- 5. ТРАНСФЕРНЫЙ РЫНОК (Inline) ---
def market_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Купить Игрока 🛒", callback_data="market_buy"))
    builder.row(InlineKeyboardButton(text="Продать Игрока 📤", callback_data="market_sell"))
    builder.row(InlineKeyboardButton(text="Мои Объявления 📣", callback_data="market_my"))
    builder.row(InlineKeyboardButton(text="Фильтры 🔍", callback_data="market_filter"))
    builder.row(InlineKeyboardButton(text="Обновить Рынок 🔄", callback_data="market_refresh"))
    builder.row(InlineKeyboardButton(text="⏪ Назад", callback_data="to_main"))
    builder.adjust(2)
    return builder.as_markup()

# --- 6. МАТЧИ (Inline) ---
def matches_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Следующий Матч 📅", callback_data="match_next"))
    builder.row(InlineKeyboardButton(text="Симулировать Матч ▶️", callback_data="match_start"))
    builder.row(InlineKeyboardButton(text="История Матчей 📜", callback_data="match_history"))
    builder.row(InlineKeyboardButton(text="Выбрать Тактику 🎯", callback_data="team_tactics"))
    builder.row(InlineKeyboardButton(text="⏪ Назад", callback_data="to_main"))
    builder.adjust(1)
    return builder.as_markup()

# --- 7. БУКМЕКЕР (Inline) ---
def bet_kb():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Сделать Ставку 💸", callback_data="bet_create"))
    builder.row(InlineKeyboardButton(text="Активные Ставки ✒️", callback_data="bet_active"))
    builder.row(InlineKeyboardButton(text="История Ставок 🧾", callback_data="bet_history"))
    builder.row(InlineKeyboardButton(text="Лидерборд 👑", callback_data="bet_leaderboard"))
    builder.row(InlineKeyboardButton(text="⏪ Назад", callback_data="to_main"))
    builder.adjust(1)
    return builder.as_markup()

# --- 8. ТАКТИКА (Inline) ---
def tactics_kb():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Агрессивный Раш 💨", callback_data="tac_rush"))
    builder.add(InlineKeyboardButton(text="Оборонительная Игра 🛡️", callback_data="tac_def"))
    builder.add(InlineKeyboardButton(text="Контроль Карты 🗺️", callback_data="tac_ctrl"))
    builder.row(InlineKeyboardButton(text="⏪ Назад", callback_data="back_to_team"))
    builder.adjust(1)
    return builder.as_markup()
