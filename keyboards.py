from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from config import TRAINING_TYPES, TACTICS

# Функция для генерации прогресс‑бара
def get_progress_bar(value: int, max_value: int = 100, width: int = 10) -> str:
    """
    Генерирует текстовый прогресс‑бар вида █░░ (заполнено/пусто)
    :param value: текущее значение
    :param max_value: максимальное значение (по умолчанию 100)
    :param width: ширина бара в символах (по умолчанию 10)
    :return: строка с прогресс‑баром
    """
    filled = int((value / max_value) * width)
    empty = width - filled
    return "█" * filled + "░" * empty

# Главное меню (ReplyKeyboardMarkup)
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            "👨‍🏫 Моя команда",
            "📈 Трансферный рынок"
        ],
        [
            "⚔️ Расписание матчей",
            "🏆 Турниры"
        ],
        [
            "💰 Букмекер",
            "📊 Статистика"
        ],
        [
            "⚙️ Настройки",
            "❓ Помощь"
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие..."
)

# Меню управления командой
def get_player_list_kb(players: list) -> InlineKeyboardMarkup:
    """
    Генерирует инлайн‑кнопки для списка игроков с отображением стамины и редкости
    :param players: список игроков из БД (каждая запись — кортеж)
    :return: InlineKeyboardMarkup с кнопками игроков
    """
    keyboard = []

    rarity_emojis = {
        "Неопытный": "🟡",
        "Опытный": "🟢",
        "Профи": "🔵",
        "Звезда": "⭐",
        "Легендарный": "👑"
    }

    for player in players:
        # player[0] — id, [2] — nickname, [4] — rarity, [8] — stamina
        player_id = player[0]
        nickname = player[2]
        rarity = player[4]
        stamina = player[8]

        # Получаем эмодзи редкости
        rarity_emoji = rarity_emojis.get(rarity, "❓")

        # Форматируем кнопку: имя | 🔋 85% | ⭐
        button_text = f"👤 {nickname} | 🔋 {stamina}% | {rarity_emoji}"

        keyboard.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"player_info_{player_id}"
            )
        ])

    # Добавляем кнопки навигации
    keyboard.append([
        InlineKeyboardButton(text="💸 Выплатить зарплату", callback_data="pay_salary"),
        InlineKeyboardButton(text="💪 Тренировки", callback_data="training_menu")
    ])
    keyboard.append([
        InlineKeyboardButton(text="🦊 Талисман команды", callback_data="choose_mascot"),
        InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu")
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def team_management_kb() -> InlineKeyboardMarkup:
    """Меню управления командой с основными действиями"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Список игроков", callback_data="team_list")],
        [InlineKeyboardButton(text="💰 Финансы команды", callback_data="team_finance")],
        [InlineKeyboardButton(text="💪 Тренировки", callback_data="training_menu")],
        [InlineKeyboardButton(text="💸 Зарплата игрокам", callback_data="pay_salary")],
        [InlineKeyboardButton(text="🦊 Талисман команды", callback_data="choose_mascot")],
        [InlineKeyboardButton(text="⬅️ Назад в главное меню", callback_data="main_menu")]
    ])

# Меню тренировок
def training_menu_kb() -> InlineKeyboardMarkup:
    """Меню тренировок с отображением цены и стата"""
    keyboard = []

    for training_name, data in TRAINING_TYPES.items():
        stat = data["stat"]
        cost = data["cost"]
        stamina_cost = data.get("stamina_cost", 0)

        # Переводим стат в читаемый формат
        stat_names = {
            "aim": "Меткость",
            "reaction": "Реакция",
            "tactics": "Тактика",
            "stamina": "Выносливость",
            "morale": "Мораль"
        }
        readable_stat = stat_names.get(stat, stat)

        # Форматируем текст кнопки: Тренировка стрельбы | +Aim | 1000 кредитов (-10 stamina)
        if stamina_cost > 0:
            button_text = f"{training_name} | +{readable_stat} | {cost} кредитов (-{stamina_cost} stamina)"
        else:
            button_text = f"{training_name} | +{readable_stat} | {cost} кредитов"

        keyboard.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"training_{training_name}"
            )
        ])

    keyboard.append([InlineKeyboardButton(text="⬅️ Назад к команде", callback_data="team_list")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Меню матчей и ставок
def match_menu_kb() -> InlineKeyboardMarkup:
    """Меню матчей с выбором тактики и симуляцией"""
    keyboard = [
        [InlineKeyboardButton(text="⚔️ Выбрать тактику", callback_data="select_tactic")],
        [InlineKeyboardButton(text="🚀 Начать симуляцию матча", callback_data="start_match")],
        [InlineKeyboardButton(text="💰 Сделать ставку", callback_data="bet_menu")],
        [InlineKeyboardButton(text="📜 История матчей", callback_data="match_history")],
        [InlineKeyboardButton(text="⬅️ Назад в главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def tactic_selection_kb() -> InlineKeyboardMarkup:
    """Клавиатура для выбора тактики матча"""
    keyboard = []

    for tactic_name in TACTICS.keys():
        risk_level = TACTICS[tactic_name]["risk"]
        multiplier = TACTICS[tactic_name]["reward_multiplier"]

        # Определяем эмодзи риска
        if risk_level >= 0.7:
            risk_emoji = "🔥"
        elif risk_level >= 0.4:
            risk_emoji = "⚠️"
        else:
            risk_emoji = "🛡️"

        button_text = f"{risk_emoji} {tactic_name} (x{multiplier})"
        keyboard.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"tactic_{tactic_name}"
            )
        ])

    keyboard.append([InlineKeyboardButton(text="⬅️ Назад к матчам", callback_data="match_menu")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def bet_menu_kb() -> InlineKeyboardMarkup:
    """Меню ставок с вариантами ставок"""
    keyboard = [
        [InlineKeyboardButton(text="🔪 Раунд на ножах", callback_data="bet_knife")],
        [InlineKeyboardButton(text="💥 Эйс в раунде", callback_data="bet_ace")],
        [InlineKeyboardButton(text="👑 Клатч 1vX", callback_data="bet_clutch")],
        [InlineKeyboardButton(text="🏆 Победа в матче", callback_data="bet_win")],
        [InlineKeyboardButton(text="⬅️ Назад к матчам", callback_data="match_menu")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Универсальное меню возврата
def back_to_main_kb() -> InlineKeyboardMarkup:
    """Универсальная кнопка возврата в главное меню"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ В главное меню", callback_data="main_menu")]
    ])

def back_to_team_kb() -> InlineKeyboardMarkup:  # <--- Добавь Markup (если пропущено) и обязательно ДВОЕТОЧИЕ
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад в меню", callback_data="main_menu")
    return builder.as_markup()
