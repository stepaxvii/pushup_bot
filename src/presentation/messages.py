"""
Message templates for Telegram bot.
"""
from datetime import date
from typing import Optional

from src.domain.entities import User, UserStats, Task


def get_welcome_message(first_name: str) -> str:
    """Get welcome message."""
    return f"""
🏋️‍♂️ Привет, {first_name}! 

Я твой персональный тренер по отжиманиям! 

💪 Готов начать тренировку? Нажми "Новое задание"!

📋 Используй кнопки ниже для навигации:
    """


def get_task_message(first_name: str, task: Task) -> str:
    """Get task message."""
    return f"""
💪 {first_name}, твое задание на сегодня:

🎯 {task.pushups_count} отжиманий
📊 Уровень: {task.level}

Выбери действие:
    """


def get_already_completed_message(first_name: str) -> str:
    """Get message when user already completed today's task."""
    return f"🎉 {first_name}, ты уже выполнил задание на сегодня! Молодец!\n\nНажми 'Моя статистика' чтобы посмотреть свой прогресс."


def get_stats_message(stats: UserStats) -> str:
    """Get statistics message."""
    first_name = stats.user_data.first_name
    
    # Получаем детальную статистику
    from src.infrastructure.database import DatabaseAdapter
    db = DatabaseAdapter()
    today_count = db.get_today_activity_count(stats.user_data.chat_id)
    detailed_stats = db.get_detailed_stats(stats.user_data.chat_id)
    
    today_status = f"✅ {today_count} отжиманий" if today_count > 0 else "❌ Не выполнено"
    
    # Форматируем даты
    first_date = detailed_stats.get('first_activity', 'Нет')
    last_date = detailed_stats.get('last_activity', 'Нет')
    
    if first_date and first_date != 'Нет':
        first_date = first_date.split(' ')[0] if ' ' in str(first_date) else str(first_date)
    if last_date and last_date != 'Нет':
        last_date = last_date.split(' ')[0] if ' ' in str(last_date) else str(last_date)
    
    return f"""
📊 Статистика {first_name}:

🎯 Уровень: {stats.user_data.level}
📅 Дней тренировок: {stats.days_count}
💪 Всего отжиманий: {stats.total_pushups}
📆 Последняя активность: {last_date}
📋 Сегодня: {today_status}

📈 Детальная статистика:
• 🗓️ Первая тренировка: {first_date}
• 📊 Среднее в день: {detailed_stats.get('avg_per_day', 0)} отжиманий
• 🔥 Дней подряд: {detailed_stats.get('consecutive_days', 0)}
• 📅 За неделю: {detailed_stats.get('week_days', 0)} дней, {detailed_stats.get('week_pushups', 0)} отжиманий
• 📅 За месяц: {detailed_stats.get('month_days', 0)} дней, {detailed_stats.get('month_pushups', 0)} отжиманий

🔥 Продолжай тренироваться!
    """


def get_no_stats_message(first_name: str) -> str:
    """Get message when user has no statistics."""
    return f"❌ {first_name}, у тебя пока нет статистики.\nНачни тренировку, нажав 'Новое задание'!"


def get_help_message() -> str:
    """Get help message."""
    return """
📚 Справка по боту:

🏋️‍♂️ Новое задание - получить задание на сегодня
📊 Моя статистика - посмотреть свой прогресс
❓ Помощь - показать эту справку
🎯 Настройки - изменить уровень сложности

💡 Как это работает:
1. Нажми "Новое задание"
2. Выполни задание
3. Нажми "✅ Выполнил" или введи другое количество
4. Следи за своим прогрессом!

🎯 Цель: делать отжимания каждый день!
    """


def get_settings_message(first_name: str, current_level: int) -> str:
    """Get settings message."""
    return f"""
🎯 Настройки {first_name}:

📊 Текущий уровень: {current_level}

Уровни сложности:
1️⃣ Начинающий (5-15 отжиманий)
2️⃣ Новичок (10-25 отжиманий)
3️⃣ Средний (15-35 отжиманий)
4️⃣ Продвинутый (20-45 отжиманий)
5️⃣ Эксперт (25-60 отжиманий)
6️⃣ Мастер (30-80 отжиманий)

Выбери новый уровень:
    """


def get_task_completed_message(first_name: str, pushups_count: int) -> str:
    """Get task completed message."""
    return f"""
🎉 Отлично, {first_name}! 

✅ Добавлено: {pushups_count} отжиманий
📅 Дата: {date.today().strftime('%d.%m.%Y')}

💪 Продолжай в том же духе!
    """


def get_task_skipped_message(first_name: str) -> str:
    """Get task skipped message."""
    return f"😔 {first_name}, ты пропустил день. Завтра обязательно сделай отжимания!"


def get_level_updated_message(first_name: str, new_level: int) -> str:
    """Get level updated message."""
    return f"""
✅ Уровень успешно изменен!

🎯 Новый уровень: {new_level}
👤 Пользователь: {first_name}

Теперь ты будешь получать задания соответствующей сложности!
    """


def get_error_message() -> str:
    """Get generic error message."""
    return "❌ Произошла ошибка. Попробуйте еще раз."


def get_invalid_input_message() -> str:
    """Get invalid input message."""
    return "❌ Неверный формат! Введи число (например: 25)"


def get_negative_number_message() -> str:
    """Get negative number message."""
    return "❌ Количество отжиманий не может быть отрицательным!"


def get_greeting_message() -> str:
    """Get greeting message."""
    return "👋 Привет! Готов к тренировке? Нажми 'Новое задание'!"


def get_thanks_message() -> str:
    """Get thanks message."""
    return "😊 Пожалуйста! Продолжай тренироваться! 💪"


def get_unknown_command_message() -> str:
    """Get unknown command message."""
    return "🤔 Используй кнопки меню для навигации или просто напиши число отжиманий!"


def get_detailed_stats_message(first_name: str, detailed_stats: dict) -> str:
    """Get detailed statistics message."""
    # Форматируем даты
    first_date = detailed_stats.get('first_activity', 'Нет')
    last_date = detailed_stats.get('last_activity', 'Нет')
    
    if first_date and first_date != 'Нет':
        first_date = first_date.split(' ')[0] if ' ' in str(first_date) else str(first_date)
    if last_date and last_date != 'Нет':
        last_date = last_date.split(' ')[0] if ' ' in str(last_date) else str(last_date)
    
    return f"""
📊 Детальная статистика {first_name}:

🎯 Уровень: {detailed_stats.get('current_level', 1)}
📅 Всего дней тренировок: {detailed_stats.get('total_days', 0)}
💪 Всего отжиманий: {detailed_stats.get('total_pushups', 0)}
📊 Среднее в день: {detailed_stats.get('avg_per_day', 0)} отжиманий
🔥 Дней подряд: {detailed_stats.get('consecutive_days', 0)}

📈 Периоды:
• 🗓️ Первая тренировка: {first_date}
• 📆 Последняя тренировка: {last_date}
• 📅 За неделю: {detailed_stats.get('week_days', 0)} дней, {detailed_stats.get('week_pushups', 0)} отжиманий
• 📅 За месяц: {detailed_stats.get('month_days', 0)} дней, {detailed_stats.get('month_pushups', 0)} отжиманий

🏆 Достижения:
• 🎯 Текущий уровень: {detailed_stats.get('current_level', 1)}
• 📈 Прогресс: {detailed_stats.get('total_pushups', 0)} отжиманий за {detailed_stats.get('total_days', 0)} дней

🔥 Продолжай тренироваться!
    """ 