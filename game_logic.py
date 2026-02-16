import random
from datetime import datetime
import config
from database import reduce_player_stamina, update_player_stats, log_random_event, add_sticker_to_collection

def calculate_team_power(players: list, tactic: str, mascot_bonus: dict) -> float:
    """
    Рассчитывает общую силу команды с учётом характеристик игроков, их усталости и бонусов.
    :param players: список игроков (из БД)
    :param tactic: выбранная тактика матча
    :param mascot_bonus: бонус от талисмана (словарь с изменениями характеристик)
    :return: общая сила команды (float)
    """
    total_power = 0.0

    for player in players:
        # player[5] — aim, [6] — reaction, [7] — tactics, [8] — stamina
        aim = player[5]
        reaction = player[6]
        tactics = player[7]
        stamina = player[8]

        # Применяем бонус талисмана к характеристикам игрока
        if 'aim' in mascot_bonus:
            aim += mascot_bonus['aim']
        if 'reaction' in mascot_bonus:
            reaction += mascot_bonus['reaction']
        if 'morale' in mascot_bonus:
            tactics += mascot_bonus['morale']  # мораль косвенно влияет на тактику

        # Корректировка силы с учётом усталости
        if stamina < 50:
            fatigue_multiplier = stamina / 50.0  # при 50 % — множитель 1.0, ниже — падает
        else:
            fatigue_multiplier = 1.0

        # Базовая сила игрока: среднее характеристик, взвешенное по важности
        player_power = (aim * 0.4 + reaction * 0.3 + tactics * 0.3) * fatigue_multiplier
        total_power += player_power

    # Применяем множитель тактики
    tactic_multiplier = config.TACTICS[tactic]["reward_multiplier"]
    total_power *= tactic_multiplier

    return round(total_power, 2)

async def simulate_match_pro(user_team: list, tactic: str, mascot_name: str) -> dict:
    """
    Симулирует матч по правилам MR12 (до 13 побед).
    :param user_team: список игроков пользователя
    :param tactic: выбранная тактика
    :param mascot_name: имя талисмана
    :return: словарь с результатом матча, счётом, логом и событиями
    """
    # Получаем бонус от талисмана
    mascot_bonus = config.MASCOTS[mascot_name]["effect"](0, 0, 0)  # передаём нули, берём только структуру

    # Сила нашей команды
    user_power = calculate_team_power(user_team, tactic, mascot_bonus)


    # Сила противника (случайная, но с учётом уровня пользователя)
    avg_player_power = user_power / len(user_team)
    enemy_power = random.uniform(
        avg_player_power * 4.5,  # мин. сила противника
        avg_player_power * 5.5   # макс. сила противника
    )

    # Счёт матча
    user_score = 0
    enemy_score = 0

    # Лог раундов и список событий
    round_log = []
    match_events = []

    # Симуляция раундов (максимум 24 раунда, пока кто‑то не наберёт 13)
    while user_score < 13 and enemy_score < 13:
        round_number = user_score + enemy_score + 1

        # Вероятность победы в раунде
        total_power = user_power + enemy_power
        win_probability = user_power / total_power

        # Определяем победителя раунда
        if random.random() < win_probability:
            user_score += 1
            round_winner = "user"
        else:
            enemy_score += 1
            round_winner = "enemy"

        # Проверяем спец‑события
        for event_type, probability in config.MATCH_EVENTS_PROBABILITIES.items():
            if random.random() < probability:
                match_events.append({
                    "type": event_type,
            "round": round_number,
            "winner": round_winner
        })

        # Записываем раунд в лог
        round_log.append(f"Раунд {round_number}: {'Победа' if round_winner == 'user' else 'Поражение'}")

    # Определяем результат матча
    result = "WIN" if user_score > enemy_score else "LOSS"

    score = f"{user_score}:{enemy_score}"

    return {
        "result": result,
        "score": score,
        "round_log": round_log,
        "match_events": match_events,
        "user_power": user_power,
        "enemy_power": enemy_power
    }

async def post_match_processing(user_id: int, result: str, players: list):
    """
    Обрабатывает последствия матча: деньги, фанаты, усталость, мораль.
    :param user_id: ID пользователя
    :param result: результат матча (WIN/LOSS)
    :param players: список игроков команды
    """
    from database import update_user_balance, get_user

    user = await get_user(user_id)
    current_balance = user[1]  # balance
    current_fans = user[2]  # fans

    # Начисление денег и фанатов
    if result == "WIN":
        money_reward = 3000
        fans_reward = 50
        morale_change = 5
    else:
        money_reward = 1000
        fans_reward = 10
        morale_change = -10

    await update_user_balance(user_id, money_reward)

    async with aiosqlite.connect("cs2_manager.db") as db:
        await db.execute(
            "UPDATE users SET fans = fans + ? WHERE user_id = ?",
            (fans_reward, user_id)
        )
        await db.commit()

    # Снижение стамины у всех игроков
    stamina_reduction = random.randint(10, 15)
    await reduce_player_stamina(user_id, stamina_reduction)

    # Обновление морали игроков (только в таблице players)
    for player in players:
        player_id = player[0]
        current_morale = player[9]  # morale
        new_morale = max(0, min(100, current_morale + morale_change))
        await update_player_stats(player_id, morale=new_morale)

    # Случайное событие после матча
    if random.random() < 0.2:  # 20 % шанс
        event = random.choice(config.RANDOM_EVENTS)
        await log_random_event(user_id, event["name"], event["description"])


        # Если событие — «Встреча с фанатами», добавляем стикер
        if event["name"] == "Встреча с фанатами":
            await add_sticker_to_collection(user_id, "Автограф команды", "обычная")

async def generate_highlights(match_events: list) -> list:
    """
    Генерирует красивые текстовые описания для хайлайтов матча.
    :param match_events: список событий матча
    :return: список текстовых описаний хайлайтов
    """
    highlights = []

    event_descriptions = {
        "нож_раунд": "🔥 В раунде {round} вся команда сражалась только ножами! Это было эпично!",
        "эйс_в_дыму": "💥 Игрок {winner} сделал ЭЙС в дыму на раунде {round}! Невероятно!",
        "клатч_1v5": "👑 На раунде {round} игрок {winner} вытащил КЛАТЧ 1v5! Триумф воли!",
        "проклятый_смок": "🌪 На раунде {round} противник использовал ПРОКЛЯТЫЙ СМОК — видимость упала до нуля!"
        }

    for event in match_events:
        winner_name = "нашей команды" if event["winner"] == "user" else "противника"
        text = event_descriptions.get(
            event["type"],
            "Необычное событие на раунде {round}: {type}!"
        )
        # Подставляем параметры в текст
        text = text.format(
            round=event["round"],
            winner=winner_name,
            type=event["type"].replace("_", " ")
        )
        highlights.append(text)

    # Если нет событий, генерируем общий хайлайт
    if not highlights:
        highlights.append("Матч прошёл без особых хайлайтов, но команда показала достойную игру!")

    return highlights

async def generate_match_report(match_result: dict, user_team: list, opponent_name: str) -> str:
    """
    Генерирует полный текстовый отчёт о матче с хайлайтами и статистикой.
    :param match_result: результат матча из simulate_match_pro
    :param user_team: список игроков команды пользователя
    :param opponent_name: имя противника
    :return: текст отчёта
    """
    report_lines = []

    # Заголовок
    result_emoji = "🎉 ПОБЕДА!" if match_result["result"] == "WIN" else "😢 ПОРАЖЕНИЕ"
    report_lines.append(f"📊 ОТЧЁТ О МАТЧЕ\n")
    report_lines.append(f"Команда: {match_result['score']} против {opponent_name}")
    report_lines.append(f"Результат: {result_emoji}\n")

    # Статистика сил
    report_lines.append(f"💪 Сила вашей команды: {match_result['user_power']:.1f}")
    report_lines.append(f"💪 Сила противника: {match_result['enemy_power']:.1f}\n")

    # Хайлайты
    highlights = await generate_highlights(match_result["match_events"])
    if highlights:
        report_lines.append("🌟 ХАЙЛАЙТЫ МАТЧА:")
        for highlight in highlights:
            report_lines.append(f"• {highlight}")
        report_lines.append("")

    # Лог раундов (первые 10 и последние 5 для краткости)
    round_log = match_result["round_log"]
    if len(round_log) <= 15:
        display_rounds = round_log
    else:
        display_rounds = round_log[:10] + ["..."] + round_log[-5:]

    report_lines.append("📋 ЛОГ РАУНДОВ:")
    for round_info in display_rounds:
        report_lines.append(round_info)

    # Итоговая сводка
    report_lines.append("\n🏁 ИТОГИ:")
    if match_result["result"] == "WIN":
        report_lines.append("✅ Команда показала отличную сыгранность!")
        report_lines.append("💰 Начислено: 3 000 кредитов")
        report_lines.append("👥 Прирост фанатов: +50")
        report_lines.append("💪 Мораль игроков повысилась на +5")
    else:
        report_lines.append("❌ Нужно проанализировать ошибки")
        report_lines.append("💰 Начислено: 1 000 кредитов")
        report_lines.append("👥 Прирост фанатов: +10")
        report_lines.append("😔 Мораль игроков снизилась на −10")

    # Информация об усталости
    stamina_reduction = random.randint(10, 15)
    report_lines.append(f"🏃 Усталость игроков: −{stamina_reduction}% у всех")

    return "\n".join(report_lines)

# Вспомогательная функция для расчёта индивидуальных шансов игрока в раунде
def calculate_player_round_chance(player: tuple, round_type: str = "normal") -> float:
    """
    Рассчитывает шанс игрока повлиять на раунд с учётом специализации.
    :param player: данные игрока
    :param round_type: тип раунда (normal, knife, clutch и т. д.)
    :return: шанс влияния (0.0–1.0)
    """
    aim = player[5]
    reaction = player[6]
    tactics = player[7]
    stamina = player[8]
    position = player[3]  # позиция

    # Базовая формула
    base_chance = (aim * 0.4 + reaction * 0.3 + tactics * 0.2) / 100

    # Бонусы по позициям
    position_bonuses = {
        "AWPer": 0.15 if round_type != "knife" else -0.2,
        "Entry Fragger": 0.1 if round_type == "normal" else 0.05,
        "Lurker": 0.12 if round_type == "clutch" else 0.0,
        "IGL": 0.1 if round_type in ["normal", "clutch"] else 0.0
    }

    bonus = position_bonuses.get(position, 0)

    # Корректировка на усталость
    fatigue_penalty = max(0, (100 - stamina) / 200)  # при 100 % — 0, при 0 % — −0.5

    final_chance = max(0.1, base_chance + bonus - fatigue_penalty)  # минимум 10 %

    return round(final_chance, 2)

# Функция для симуляции ключевых моментов раунда (для более глубокой проработки)
async def simulate_key_moment(player_id: int, moment_type: str) -> dict:
    """
    Симулирует ключевой момент раунда (эйс, клатч и т. д.).
    :param player_id: ID игрока
    :param moment_type: тип момента
    :return: словарь с результатом и описанием
    """
    from database import get_team_players

    players = await get_team_players(player_id)
    player = next((p for p in players if p[0] == player_id), None)

    if not player:
        return {"success": False, "description": "Игрок не найден"}

    chance = calculate_player_round_chance(player, moment_type)

    success = random.random() < chance

    descriptions = {
        "ace": [
            "Невероятный ЭЙС от {nickname}! Все пять противников упали!",
            "{nickname} — мастер стрельбы! Пять фрагов подряд!",
            "ЭЙС в исполнении {nickname}! Зал аплодирует!"
        ],
        "clutch": [
            "Немыслимый КЛАТЧ 1v5 от {nickname}!",
            "{nickname} вытащил невозможное! 1 против 5!",
            "Триумф воли: {nickname} победил в клатче 1v5!"
        ]
    }

    if success and moment_type in descriptions:
        desc_list = descriptions[moment_type]
        description = random.choice(desc_list).format(nickname=player[2])  # player[2] — nickname
    else:
        description = f"{player[2]} пытался сделать {moment_type}, но не получилось."

    return {
        "success": success,
        "description": description,
        "chance": chance
    }
    