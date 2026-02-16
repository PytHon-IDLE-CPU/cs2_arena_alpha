# config.py
API_TOKEN = "8558553503:AAH6FdDAx_uqqLFt4hGsseBZ1cPUXSs5A8g"
DB_PATH = "cs2_arena.db"
ADMIN_ID = 5056869104 # Ваш Telegram ID

# Ники игроков
NICKS = [
    "ShadowStrike", "Pryanichek", "CyberBullet", "FrostNovaX", "CheburekPro",
    "X-God", "SilentReaper", "BorshMaster", "NeonPhantom", "ShaurmaKing",
    "ApexPredator", "KefirKiller", "VoidWalker", "PelmeniPro", "QuantumRush",
    "SousChef", "MidnightFox", "VarenikBoss"
]

# Дивизионы
DIVISIONS = [
    ("Подвальные Воины", "Даже в подвале рождаются чемпионы — поднимайся, пока другие спят!"),
    ("Мастера Компьютерных Клубов", "Ты уже не новичок, но твой потенциал — за пределами этих клубов. Время идти выше!"),
    ("Региональные Ассы", "Локальная слава — только начало. Покажи, что твой талант не знает границ!"),
    ("Национальные Звёзды", "Ты уже на вершине страны, но настоящая легенда рождается там, где боятся подняться!"),
    ("Бессмертные Легенды", "Ты вошёл в историю. Но даже легенды продолжают писать свои эпопеи — не останавливайся!")
]

# Фразы Алисы для матчей
MATCH_EVENTS = [
    "Эйс!", "Промах!", "Ниндзя-дифьюз!", "Снайпер снайпит!", "Минус 5 — это ты?",
    "Идеальный выход на B!", "Скок в голову!", "Сделал килл в последнюю секунду!"
]

MAPS = ["Dust2", "Mirage", "Inferno"]

# Параметры тренировок
TRAINING_OPTIONS = [
    ("Стрельба по тарелочкам", 3, 2, 0, 0, 20),
    ("Просмотр демок под чипсы", 0, 1, 2, 1, 10),
    ("Турнир на ножах 1x1", 0, 3, 0, 0, 15),
    ("Гонка за курицами", 2, 0, 0, 5, 15),
    ("Дефьюз вслепую", 0, 0, 3, 2, 20)
]

# Стоимость ставок и награды
ACE_BET_COST = 500
ACE_BET_WIN = 1750
MATCH_REWARD_COINS = 1500
MATCH_REWARD_FANS = 100
MATCH_PENALTY_MORALE = 10
ENERGY_LOSS_PER_MATCH = 15
ENERGY_RESTORE_INTERVAL = 1800  # 30 минут
ENERGY_RESTORE_AMOUNT = 5
CASE_COST = 500

# Система скинов
SKINS = [
    ("Blue Skin", "Common", 5),
    ("Purple Skin", "Epic", 10),
    ("Pink Skin", "Mythical", 15),
    ("Red Skin", "Legendary", 20),
    ("Gold Skin", "Exceedingly Rare", 25)
]



