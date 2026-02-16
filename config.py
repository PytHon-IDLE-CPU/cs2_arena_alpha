import os

# Берем токен из переменных окружения Railway
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Настройки экономики
START_BALANCE = 50000
CASE_PRICE = 2500
TRAINING_COST = 1000  # Добавь, если Алиса использовала это название
BOOST_CAMP_COST = 10000 

# Зарплаты по редкости игроков
SALARY_BY_RARITY = {
    "Неопытный": 500,
    "Опытный": 1500,
    "Профи": 3000,
    "Звезда": 6000,
    "Легендарный": 12000,
    }

# Словари талисманов и их эффектов
MASCOTS = {
    "Волк": {
        "bonus": "Сыгранность +10% (Aim +5, Reaction +5)",
        "effect": lambda aim, reaction, morale: {"aim": aim + 5, "reaction": reaction + 5, "morale": morale}
    },
    "Орёл": {
        "bonus": "Реакция +5",
        "effect": lambda aim, reaction, morale: {"aim": aim, "reaction": reaction + 5, "morale": morale}
    },
    "Дракон": {
        "bonus": "Мораль +15",
        "effect": lambda aim, reaction, morale: {"aim": aim, "reaction": reaction, "morale": morale + 15}
    },
    "Кот": {
        "bonus": "Удача +10% (шанс двойного выпадения кейса)",
        "effect": lambda aim, reaction, morale: {"aim": aim, "reaction": reaction, "morale": morale}
    }
}

# Спонсоры и их условия
SPONSORS = {
    "Logitech": {
        "weekly_payment": 500,
        "condition": "3 победы подряд",
        "penalty": 200  # штраф за невыполнение
    },
    "Red Bull": {
        "weekly_payment": 2000,
        "condition": "5+ матчей в месяц",
        "penalty": 500
    },
    "Nike": {
        "weekly_payment": 1000,
        "condition": "рейтинг команды > 50",
        "penalty": 300
    }
}

# Список карт CS2
MAPS = [
    "Dust II",
    "Mirage",
    "Inferno",
    "Nuke",
    "Overpass",
    "Vertigo",
    "Ancient"
]

# Пул случайных событий между матчами
RANDOM_EVENTS = [
    {
        "name": "Загул в клубе",
        "description": "Игроки устроили вечеринку после победы. Мораль +20, но усталость +15%",
        "morale_change": 20,
        "stamina_change": -15
    },
    {
        "name": "Ссора в команде",
        "description": "Два игрока поссорились из‑за тактики. Мораль −15 у обоих",
        "morale_change": -15,
        "affected_players": 2
    },
    {
        "name": "Встреча с фанатами",
        "description": "Автографы и фото подняли мораль команды!",
        "morale_change": 10
    },
    {
        "name": "Травма на тренировке",
        "description": "Игрок повредил руку. −20% к меткости на 3 матча",
        "aim_change": -20,
        "duration": 3
    },
    {
        "name": "Вдохновляющая речь",
        "description": "Вы провели мотивационную беседу. Мораль +15 у всех игроков",
        "morale_change": 15
    }
]

# Тактики матчей и их множители
TACTICS = {
    "Агрессивный раш": {"risk": 0.8, "reward_multiplier": 1.5},
    "Оборонительная игра": {"risk": 0.3, "reward_multiplier": 0.8},
    "Контроль карты": {"risk": 0.5, "reward_multiplier": 1.2},
    "Хитрые ловушки": {"risk": 0.6, "reward_multiplier": 1.3}
}

# Типы тренировок и их параметры
TRAINING_TYPES = {
    "Тренировка стрельбы": {"stat": "aim", "cost": 1000, "time_hours": 12, "stamina_cost": 10},
    "Тактический сбор": {"stat": "tactics", "cost": 1500, "time_hours": 24, "stamina_cost": 15},
    "Физическая подготовка": {"stat": "stamina", "cost": 800, "time_hours": 8, "stamina_cost": 5},
    "Мотивационная речь": {"stat": "morale", "cost": 500, "time_hours": 4, "stamina_cost": 0}
}

# Позиции игроков
POSITIONS = ["Rifle", "AWPer", "Entry Fragger", "Support", "Lurker", "IGL"]

# Редкости игроков
RARITIES = ["Неопытный", "Опытный", "Профи", "Звезда", "Легендарный"]

# Никнеймы для генерации случайных игроков
NICKS = [
    "X-God", "Pryanichek", "CyberBullet", "FrostNovaX", "CheburekPro",
    "SilentReaper", "BorshMaster", "NeonPhantom", "ShaurmaKing", "ApexPredator",
    "KefirKiller", "VoidWalker", "PelmeniPro", "QuantumRush", "SousChef",
    "MidnightFox", "VarenikBoss", "StormBreaker", "BlinchikiOP", "ShadowStrike"
]

# Вероятности особых событий в матче
MATCH_EVENTS_PROBABILITIES = {
    "нож_раунд": 0.05,  # 5% шанс раунда только с ножами
    "эйс_в_дыму": 0.1,  # 10% шанс эпичного эйса
    "клатч_1v5": 0.02,  # 2% шанс невероятного клатча
    "проклятый_смок": 0.03  # 3% шанс особого смока
}


