import asyncio
import random
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

import config
import database
import keyboards
import game_logic

# Инициализация бота и диспетчера
bot = Bot(token=config.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Состояния FSM
class GameStates(StatesGroup):
    waiting_for_team_name = State()
    training_player = State()
    selecting_tactic = State()
    opening_case = State()

# Хэндлер команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """
    Обрабатывает команду /start.
    Если пользователя нет в базе — запрашивает название команды.
    Если есть — показывает главное меню.
    """
    user_id = message.from_user.id
    user = await database.get_user(user_id)

    if user is None:
        # Пользователь новый — запрашиваем название команды
        await message.answer(
            "👋 Добро пожаловать в CS2 Manager!\n\n"
            "Вы назначены менеджером новой киберспортивной команды.\n"
            "Как будет называться ваша команда?"
        )
        await state.set_state(GameStates.waiting_for_team_name)
    else:
        # Пользователь уже есть в базе — показываем главное меню
        await message.answer(
            f"👋 Добро пожаловать обратно, менеджер!\n"
            f"Ваша команда: *{user[2]}*\n\n"
            "Выберите действие:",
            reply_markup=keyboards.main_menu,
            parse_mode="Markdown"
        )

# Хэндлер ввода названия команды
@dp.message(GameStates.waiting_for_team_name, F.text)
async def process_team_name(message: types.Message, state: FSMContext):
    """
    Сохраняет название команды в БД и выдаёт «Кейс новичка» с 5 игроками.
    """
    team_name = message.text.strip()
    user_id = message.from_user.id

    # Создаём пользователя в БД
    await database.create_user(user_id, team_name)

    # Генерируем 5 случайных игроков для «Кейса новичка»
    rarities = list(config.SALARY_BY_RARITY.keys())
    positions = ["AWPer", "Entry Fragger", "Lurker", "IGL", "Support"]

    for i in range(5):
        # Генерируем характеристики игрока
        rarity = random.choice(rarities)
        position = positions[i]
        nickname = f"Игрок_{i+1}"

        # Базовые характеристики в зависимости от редкости
        base_stats = {
            "Неопытный": (40, 40, 40),
            "Опытный": (55, 55, 50),
            "Профи": (70, 65, 60),
            "Звезда": (85, 75, 70),
            "Легендарный": (95, 85, 80)
        }
        aim, reaction, tactics = base_stats[rarity]

        # Добавляем небольшой случайный разброс характеристик (±10)
        aim += random.randint(-10, 10)
        reaction += random.randint(-10, 10)
        tactics += random.randint(-10, 10)

        # Ограничиваем характеристики диапазоном 30–100
        aim = max(30, min(100, aim))
        reaction = max(30, min(100, reaction))
        tactics = max(30, min(100, tactics))

        # Создаём игрока в БД
        await database.add_player(
            owner_id=user_id,
            nickname=nickname,
            position=position,
            rarity=rarity
        )

        # Сразу обновляем его характеристики
        players = await database.get_team_players(user_id)
        player_id = [p[0] for p in players if p[2] == nickname][0]
        await database.update_player_stats(
            player_id,
            aim=aim,
            reaction=reaction,
            tactics=tactics,
            stamina=100,
            morale=80
        )

    # Получаем обновлённый список игроков для отображения
    players = await database.get_team_players(user_id)
    player_list_text = "\n".join([f"• {p[2]} ({p[4]}) — {p[3]}" for p in players])

    # Отправляем поздравление и список игроков
    welcome_text = (
        f"🎉 Поздравляем, менеджер! Вы успешно создали команду **«{team_name}»**!\n\n"
        f"🎁 Вам выпал «Кейс новичка» — вот 5 игроков, готовых к бою:\n\n{player_list_text}\n\n"
        f"💰 Баланс: {config.START_BALANCE} кредитов\n"
        f"👥 Фанаты: 0\n"
        f"🏆 Репутация: 50\n\n"
        "Используйте главное меню, чтобы управлять командой, тренироваться и играть матчи!"
    )

    await message.answer(welcome_text, parse_mode="Markdown", reply_markup=keyboards.main_menu)

    # Сбрасываем состояние
    await state.clear()

# Запуск бота
async def main():
    # Инициализируем базу данных
    await database.init_db()
    print("База данных инициализирована")

    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    # Хэндлер просмотра списка игроков (team_list)
@dp.callback_query(F.data == "team_list")
async def show_team_list(callback: types.CallbackQuery):
    """
    Показывает список игроков команды с их статами и стаминой.
    Использует функцию из keyboards.py для генерации клавиатуры.
    """
    user_id = callback.from_user.id
    players = await database.get_team_players(user_id)

    if not players:
        await callback.message.edit_text(
            "😞 У вас пока нет игроков в команде.\n"
            "Используйте «Кейс новичка» или покупайте игроков на рынке!",
            reply_markup=keyboards.main_menu
        )
        return

    # Генерируем текст списка игроков
    team_text = "👥 Ваша команда:\n\n"
    for player in players:
        # player[0] — ID, [2] — nickname, [3] — position, [4] — rarity,
        # [5] — aim, [6] — reaction, [7] — tactics, [8] — stamina, [9] — morale
        team_text += (
            f"• **{player[2]}** ({player[4]})\n"
            f"  Позиция: {player[3]} | "
            f"Стрельба: {player[5]} | "
            f"Реакция: {player[6]} | "
            f"Тактика: {player[7]}\n"
            f"  🔋 Стамина: {player[8]}% | "
            f"💪 Мораль: {player[9]}%\n\n"
        )

    # Используем клавиатуру из keyboards.py
    team_keyboard = keyboards.create_team_keyboard(players)

    await callback.message.edit_text(
        team_text,
        parse_mode="Markdown",
        reply_markup=team_keyboard
    )
    await callback.answer()

# Хэндлер детальной информации об игроке (player_info_{id})
@dp.callback_query(F.data.startswith("player_info_"))
async def show_player_info(callback: types.CallbackQuery):
    """
    Показывает детальную карточку игрока с кнопками "Тренировать" и "Продать".
    """
    player_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id

    player = await database.get_player(player_id)
    if not player or player[1] != user_id:  # проверяем, что игрок принадлежит пользователю
        await callback.answer("❌ Игрок не найден или не принадлежит вам.", show_alert=True)
        return

    # Формируем карточку игрока
    player_info = (
        f"👤 **{player[2]}**\n"
        f"Позиция: {player[3]}\n"
        f"Редкость: {player[4]}\n"
        f"💰 Зарплата: {config.SALARY_BY_RARITY[player[4]]} кредитов/матч\n\n"
        f"**Характеристики:**\n"
        f"🎯 Стрельба (Aim): {player[5]}\n"
        f"⚡ Реакция (Reaction): {player[6]}\n"
        f"🧠 Тактика (Tactics): {player[7]}\n"
        f"🔋 Стамина: {player[8]}%\n"
        f"💪 Мораль: {player[9]}%\n\n"
        f"*Используйте кнопки ниже для действий с игроком.*"
    )

    # Создаём клавиатуру с действиями
    player_keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="🏋️ Тренировать", callback_data=f"train_player_{player_id}"),
            types.InlineKeyboardButton(text="💸 Продать", callback_data=f"sell_player_{player_id}")
        ],
        [types.InlineKeyboardButton(text="◀️ Назад к списку", callback_data="team_list")]
    ])


    await callback.message.edit_text(
        player_info,
        parse_mode="Markdown",
        reply_markup=player_keyboard
    )
    await callback.answer()

# Раздел тренировок
@dp.callback_query(F.data.startswith("train_player_"))
async def start_training(callback: types.CallbackQuery, state: FSMContext):
    """
    Начинает процесс тренировки игрока: показывает типы тренировок и проверяет баланс.
    """
    player_id = int(callback.data.split("_")[2])
    user_id = callback.from_user.id

    player = await database.get_player(player_id)
    if not player or player[1] != user_id:
        await callback.answer("❌ Игрок не найден.", show_alert=True)
        return

    user = await database.get_user(user_id)
    balance = user[1]  # баланс пользователя

    # Проверяем, хватает ли денег на тренировку
    training_cost = config.TRAINING_COST
    if balance < training_cost:
        await callback.answer(
            f"❌ Недостаточно средств для тренировки!\n"
            f"Требуется: {training_cost} кредитов\n"
            f"У вас: {balance} кредитов",
            show_alert=True
        )
        return

    # Сохраняем ID игрока в состоянии для следующего шага
    await state.update_data(training_player_id=player_id)

    # Показываем типы тренировок
    training_keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="🎯 Улучшить стрельбу (+5 Aim)", callback_data="train_aim"),
            types.InlineKeyboardButton(text="⚡ Улучшить реакцию (+5 Reaction)", callback_data="train_reaction")
        ],
        [
            types.InlineKeyboardButton(text="🧠 Улучшить тактику (+5 Tactics)", callback_data="train_tactics"),
            types.InlineKeyboardButton(text="💪 Восстановить мораль (+10 Morale)", callback_data="restore_morale")
        ],
        [types.InlineKeyboardButton(text="◀️ Отмена", callback_data="player_info_" + str(player_id))]
    ])

    await callback.message.edit_text(
        f"🏋️ Выберите тип тренировки для {player[2]}:\n"
        f"Стоимость: {training_cost} кредитов",
        parse_mode="Markdown",
        reply_markup=training_keyboard
    )
    await state.set_state(GameStates.training_player)
    await callback.answer()

@dp.callback_query(GameStates.training_player, F.data.in_(["train_aim", "train_reaction", "train_tactics", "restore_morale"]))
async def process_training(callback: types.CallbackQuery, state: FSMContext):
    """
    Обрабатывает выбор типа тренировки, списывает деньги и обновляет статы игрока.
    """
    data = await state.get_data()
    player_id = data["training_player_id"]
    user_id = callback.from_user.id

    training_type = callback.data
    training_cost = config.TRAINING_COST

    # Списываем деньги
    await database.update_user_balance(user_id, -training_cost)

    # Обновляем характеристики игрока
    updates = {}
    if training_type == "train_aim":
        updates["aim"] = "+5"
        message_text = "✅ Улучшена стрельба!"
    elif training_type == "train_reaction":
        updates["reaction"] = "+5"
        message_text = "✅ Улучшена реакция!"
    elif training_type == "train_tactics":
        updates["tactics"] = "+5"
        message_text = "✅ Улучшена тактика!"
    else:  # restore_morale
        updates["morale"] = "+10"
# ... тут заканчивается предыдущая функция
    message_text = "✅ Мораль восстановлена!"
    # Убедись, что здесь нет лишних открытых блоков

# Эти две строки должны быть ПРИЖАТЫ К ЛЕВОМУ КРАЮ
@dp.callback_query(F.data == "start_match")
async def start_match_simulation(callback: types.CallbackQuery, state: FSMContext):
    """
    Начинает симуляцию матча...
    """
    user_id = callback.from_user.id
    # ... дальше остальной код
    players = await database.get_team_players(user_id)

    if len(players) < 5:
        await callback.message.edit_text(
            "❌ Для матча нужно 5 игроков в команде!\n"
            "Перейдите в «Трансферный рынок» или откройте кейсы, чтобы пополнить состав.",
            reply_markup=keyboards.main_menu
        )
        await callback.answer()
        return

    # Переводим в состояние выбора тактики и показываем клавиатуру тактик
    await state.set_state(GameStates.selecting_tactic)
    tactics_keyboard = keyboards.create_tactics_keyboard()

    await callback.message.edit_text(
        "🚀 Выберите тактику для предстоящего матча:",
        reply_markup=tactics_keyboard
    )
    await callback.answer()

@dp.callback_query(GameStates.selecting_tactic, F.data.startswith("tactic_"))
async def process_tactic_selection(callback: types.CallbackQuery, state: FSMContext):
    """
    Обрабатывает выбор тактики, запускает симуляцию матча и отправляет отчёт.
    """
    tactic = callback.data.split("_")[1]  # например, "aggressive"
    user_id = callback.from_user.id

    # Получаем команду игрока
    players = await database.get_team_players(user_id)
    mascot_name = "Default"  # можно добавить выбор талисмана позже

    # Запускаем симуляцию матча
    match_result = await game_logic.simulate_match_pro(players, tactic, mascot_name)

    # Генерируем красивый отчёт о матче
    opponent_name = f"Команда {random.choice(['Alpha', 'Beta', 'Gamma', 'Delta'])}"
    match_report = await game_logic.generate_match_report(match_result, players, opponent_name)

    # Отправляем отчёт пользователю
    await callback.message.answer(match_report, parse_mode="Markdown")

    # Обрабатываем последствия матча (деньги, фанаты, усталость, мораль)
    await game_logic.post_match_processing(user_id, match_result["result"], players)

    # Если была ставка, проверяем её результат
    bet = await database.get_active_bet(user_id)
    if bet and match_result["result"] == "WIN":
        # Удваиваем ставку и начисляем выигрыш
        win_amount = bet["amount"] * 2
        await database.update_user_balance(user_id, win_amount)
        await database.clear_bet(user_id)  # очищаем ставку
        await callback.message.answer(
            f"🎉 Ваша ставка сыграла! Вы выиграли {win_amount} кредитов!",
            parse_mode="Markdown"
        )

    # Возвращаем в главное меню
    await callback.message.answer("Главное меню:", reply_markup=keyboards.main_menu)
    await state.clear()
    await callback.answer()

# Система зарплат
@dp.callback_query(F.data == "pay_salary")
async def pay_team_salary(callback: types.CallbackQuery):
    """
    Списывает зарплату всех игроков команды. Если денег не хватает — снижает мораль.
    """
    user_id = callback.from_user.id
    players = await database.get_team_players(user_id)

    total_salary = sum(config.SALARY_BY_RARITY[player[4]] for player in players)
    user = await database.get_user(user_id)
    balance = user[1]

    if balance >= total_salary:
        # Списываем зарплату
        await database.update_user_balance(user_id, -total_salary)
        await callback.message.answer(
            f"✅ Зарплата выплачена!\n"
            f"Всего списано: {total_salary} кредитов\n"
            f"Остаток: {balance - total_salary} кредитов"
        )
    else:
        # Не хватает денег — снижаем мораль всем игрокам
        for player in players:
            player_id = player[0]
            current_morale = player[9]
            new_morale = max(0, current_morale - 20)
            await database.update_player_stats(player_id, morale=new_morale)

        await callback.message.answer(
            f"❌ Недостаточно средств для выплаты зарплаты!\n"
            f"Команда недовольна — мораль всех игроков снижена на 20 пунктов."
        )

    await callback.message.answer("Главное меню:", reply_markup=keyboards.main_menu)
    await callback.answer()

# Секция «Букмекер»
@dp.callback_query(F.data == "bookmaker")
async def show_bookmaker(callback: types.CallbackQuery, state: FSMContext):
    """
    Показывает интерфейс букмекера и позволяет сделать ставку на победу.
    """
    user_id = callback.from_user.id
    user = await database.get_user(user_id)
    balance = user[1]

    bookmaker_keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="💰 Ставка 100 кредитов", callback_data="bet_100"),
            types.InlineKeyboardButton(text="💰 Ставка 500 кредитов", callback_data="bet_500")
        ],
        [
            types.InlineKeyboardButton(text="💰 Ставка 1 000 кредитов", callback_data="bet_1000"),
            types.InlineKeyboardButton(text="◀️ Назад", callback_data="main_menu")
        ]
    ])

    await callback.message.edit_text(
        f"💰 Букмекерская контора\n\n"
        f"Сделайте ставку на победу в следующем матче.\n"
        f"При выигрыше ставка удваивается!\n\n"
        f"Ваш баланс: {balance} кредитов",
        reply_markup=bookmaker_keyboard
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("bet_"))
async def process_bet(callback: types.CallbackQuery):
    """
    Обрабатывает ставку пользователя и сохраняет её в БД.
    """
    amount = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    user = await database.get_user(user_id)
    balance = user[1]

    if amount > balance:
        await callback.answer("❌ Недостаточно средств для ставки!", show_alert=True)
        return

    # Сохраняем ставку в БД
    await database.create_bet(user_id, amount)

    await callback.message.edit_text(
        f"✅ Ставка принята!\n"
        f"Вы поставили {amount} кредитов на победу.\n"
        f"Если выиграете — получите {amount * 2} кредитов!\n\n"
        f"Главное меню:",
        reply_markup=keyboards.main_menu
    )
    await callback.answer()

# Запуск бота
async def main():
    # Инициализируем базу данных
    await database.init_db()
    print("База данных инициализирована")

    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    # Раздел «Трансферный рынок»
@dp.callback_query(F.data == "transfer_market")
async def show_transfer_market(callback: types.CallbackQuery):
    """
    Показывает список доступных для покупки игроков на трансферном рынке.
    """
    user_id = callback.from_user.id
    user = await database.get_user(user_id)
    balance = user[1]

    # Генерируем 3 случайных игрока для рынка
    market_players = []
    rarities = list(config.SALARY_BY_RARITY.keys())
    positions = ["AWPer", "Entry Fragger", "Lurker", "IGL", "Support"]

    for _ in range(3):
        rarity = random.choice(rarities)
        position = random.choice(positions)
        nickname = f"Свободный агент #{random.randint(1000, 9999)}"

        # Характеристики в зависимости от редкости
        base_stats = {
            "Неопытный": (40, 40, 40),
            "Опытный": (55, 55, 50),
            "Профи": (70, 65, 60),
            "Звезда": (85, 75, 70),
            "Легендарный": (95, 85, 80)
        }
        aim, reaction, tactics = base_stats[rarity]

        price = config.SALARY_BY_RARITY[rarity] * 10  # цена = зарплата × 10

        market_players.append({
            "nickname": nickname,
            "position": position,
            "rarity": rarity,
            "aim": aim,
            "reaction": reaction,
            "tactics": tactics,
            "price": price
        })

    # Сохраняем игроков рынка в БД для текущего пользователя
    await database.set_market_players(user_id, market_players)

    # Формируем сообщение
    market_text = "🏪 Трансферный рынок\n\n"
    for i, player in enumerate(market_players, 1):
        market_text += (
            f"{i}. **{player['nickname']}**\n"
            f"Позиция: {player['position']} | Редкость: {player['rarity']}\n"
            f"Стрельба: {player['aim']} | Реакция: {player['reaction']} | Тактика: {player['tactics']}\n"
            f"💰 Цена: {player['price']} кредитов\n\n"
        )

    market_keyboard = keyboards.create_market_keyboard(market_players)

    await callback.message.edit_text(
        market_text,
        parse_mode="Markdown",
        reply_markup=market_keyboard
    )
    await callback.answer()

@dp.callback_query(F.data.startswith("buy_player_"))
async def buy_player_from_market(callback: types.CallbackQuery):
    """
    Обрабатывает покупку игрока с трансферного рынка.
    """
    player_index = int(callback.data.split("_")[2])
    user_id = callback.from_user.id

    market_players = await database.get_market_players(user_id)
    if not market_players or player_index >= len(market_players):
        await callback.answer("❌ Игрок недоступен.", show_alert=True)
        return

    player = market_players[player_index]
    price = player["price"]
    user = await database.get_user(user_id)
    balance = user[1]

    if balance < price:
        await callback.answer(f"❌ Недостаточно средств! Требуется: {price} кредитов.", show_alert=True)
        return

    # Покупаем игрока
    await database.update_user_balance(user_id, -price)
    await database.add_player(
        owner_id=user_id,
        nickname=player["nickname"],
        position=player["position"],
        rarity=player["rarity"]
    )

    players = await database.get_team_players(user_id)
    player_id = [p[0] for p in players if p[2] == player["nickname"]][0]
    await database.update_player_stats(
        player_id,
        aim=player["aim"],
        reaction=player["reaction"],
        tactics=player["tactics"],
        stamina=100,
        morale=80
    )

    await callback.message.edit_text(
        f"✅ Игрок **{player['nickname']}** успешно куплен!\n"
        f"Списано: {price} кредитов\n"
        f"Остаток: {balance - price} кредитов",
        parse_mode="Markdown",
        reply_markup=keyboards.main_menu
    )
    await callback.answer()

# Раздел «Открыть кейс»
@dp.callback_query(F.data == "open_case")
async def open_case(callback: types.CallbackQuery, state: FSMContext):
    """
    Позволяет открыть кейс с шансом получить игрока разной редкости.
    """
    user_id = callback.from_user.id
    user = await database.get_user(user_id)
    balance = user[1]

    case_cost = config.CASE_COST
    if balance < case_cost:
        await callback.answer(f"❌ Недостаточно средств для открытия кейса! Требуется: {case_cost} кредитов.", show_alert=True)
        return

    # Списываем стоимость кейса
    await database.update_user_balance(user_id, -case_cost)

    # Определяем редкость выпавшего игрока
    rarity_weights = [
        ("Неопытный", 50),
        ("Опытный", 30),
        ("Профи", 15),
        ("Звезда", 4),
        ("Легендарный", 1)
    ]
    rarity = random.choices(
        [r[0] for r in rarity_weights],
        weights=[r[1] for r in rarity_weights]
    )[0]

    # Генерируем игрока
    positions = ["AWPer", "Entry Fragger", "Lurker", "IGL", "Support"]
    position = random.choice(positions)
    nickname = f"Кейсовый игрок #{random.randint(1000, 9999)}"

    base_stats = {
        "Неопытный": (40, 40, 40),
        "Опытный": (55, 55, 50),
        "Профи": (70, 65, 60),
        "Звезда": (85, 75, 70),
        "Легендарный": (95, 85, 80)
    }
    aim, reaction, tactics = base_stats[rarity]

    # Добавляем случайный разброс характеристик
    aim += random.randint(-5, 5)
    reaction += random.randint(-5, 5)
    tactics += random.randint(-5, 5)

    # Создаём игрока в БД
    await database.add_player(user_id, nickname, position, rarity)
    players = await database.get_team_players(user_id)
    player_id = [p[0] for p in players if p[2] == nickname][0]
    await database.update_player_stats(player_id, aim=aim, reaction=reaction, tactics=tactics, stamina=100, morale=80)

    # Отправляем сообщение о выпавшем игроке
    case_result = (
        f"🎁 Вы открыли кейс!\n\n"
        f"🎉 Вам выпал **{rarity}** игрок:\n"
        f"**{nickname}** ({position})\n"
        f"Стрельба: {aim} | Реакция: {reaction} | Тактика: {tactics}\n\n"
        # Завершение хендлера открытия кейса
@dp.callback_query(F.data == "open_case")
async def open_case(callback: types.CallbackQuery, state: FSMContext):
    """
    Позволяет открыть кейс с шансом получить игрока разной редкости.
    """
    user_id = callback.from_user.id
    user = await database.get_user(user_id)
    balance = user[1]

    case_cost = config.CASE_COST
    if balance < case_cost:
        await callback.answer(f"❌ Недостаточно средств для открытия кейса! Требуется: {case_cost} кредитов.", show_alert=True)
        return


    # Списываем стоимость кейса
    await database.update_user_balance(user_id, -case_cost)

    # Определяем редкость выпавшего игрока
    rarity_weights = [
        ("Неопытный", 50),
        ("Опытный", 30),
        ("Профи", 15),
        ("Звезда", 4),
        ("Легендарный", 1)
    ]
    rarity = random.choices(
        [r[0] for r in rarity_weights],
        weights=[r[1] for r in rarity_weights]
    )[0]

    # Генерируем игрока
    positions = ["AWPer", "Entry Fragger", "Lurker", "IGL", "Support"]
    position = random.choice(positions)
    nickname = f"Кейсовый игрок #{random.randint(1000, 9999)}"

    base_stats = {
        "Неопытный": (40, 40, 40),
        "Опытный": (55, 55, 50),
        "Профи": (70, 65, 60),
        "Звезда": (85, 75, 70),
        "Легендарный": (95, 85, 80)
    }
    aim, reaction, tactics = base_stats[rarity]

    # Добавляем случайный разброс характеристик
    aim += random.randint(-5, 5)
    reaction += random.randint(-5, 5)
    tactics += random.randint(-5, 5)

    # Создаём игрока в БД
    await database.add_player(user_id, nickname, position, rarity)
    players = await database.get_team_players(user_id)
    player_id = [p[0] for p in players if p[2] == nickname][0]
    await database.update_player_stats(player_id, aim=aim, reaction=reaction, tactics=tactics, stamina=100, morale=80)

    # Отправляем сообщение о выпавшем игроке
    case_result = (
        f"🎁 Вы открыли кейс!\n\n"
        f"🎉 Вам выпал **{rarity}** игрок:\n"
        f"**{nickname}** ({position})\n"
        f"Стрельба: {aim} | Реакция: {reaction} | Тактика: {tactics}\n\n"
        f"💰 Осталось: {balance - case_cost} кредитов"
    )

    # Клавиатура с вариантами действий
    case_keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="🎁 Открыть ещё раз", callback_data="open_case"),
            types.InlineKeyboardButton(text="🏠 В главное меню", callback_data="main_menu")
        ]
    ])

    await callback.message.edit_text(
        case_result,
        parse_mode="Markdown",
        reply_markup=case_keyboard
    )
    await callback.answer()

# Команда /help
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """
    Короткая справка по командам бота.
    """
    help_text = (
        "📖 **Справка по командам**\n\n"
        "🤖 Основные команды:\n"
        "/start — Начать игру / Вернуться в главное меню\n"
        "/help — Эта справка\n\n"
        "👥 Управление командой:\n"
        "• Просмотр состава — кнопка «👥 Состав команды»\n"
        "• Информация об игроке — выберите игрока из списка\n"
        "• Тренировка — кнопка «🏋️ Тренировать» в карточке игрока\n\n"
        "⚽ Матчи:\n"
        "• Начать матч — кнопка «🚀 Начать симуляцию матча»\n"
        "• Выбрать тактику — после начала матча\n\n"
        "💰 Финансы:\n"
        "• Выплатить зарплату — кнопка «💰 Выплатить зарплату»\n"
        "• Букмекер — кнопка «💰 Букмекер»\n\n"
        "🛍️ Покупки:\n"
        "• Трансферный рынок — кнопка «🏪 Трансферный рынок»\n"
        "• Открыть кейс — кнопка «🎁 Открыть кейс»\n\n"
        "Если возникли проблемы — напишите @admin"
    )

    await message.answer(help_text, parse_mode="Markdown")

# Обработка ошибок и запуск бота
async def main():
    try:
        # Инициализируем базу данных
        await database.init_db()
        print("База данных инициализирована")

        # Запускаем бота
        print("Бот запущен и готов к работе!")
        await dp.start_polling(bot)

    except Exception as e:
        print(f"Критическая ошибка: {e}")
        print("Попытка перезапуска через 10 секунд...")
        await asyncio.sleep(10)
        await main()  # рекурсивный перезапуск при ошибке

if __name__ == "__main__":

    asyncio.run(main())
