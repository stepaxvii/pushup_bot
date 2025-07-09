import logging
import random
from datetime import datetime, date, timedelta


# Новые функции для системы уровней

async def send_morning_reminder(bot, chat_id, first_name):
    """Отправка утреннего напоминания о тренировке."""
    try:
        from src.infrastructure.database import DatabaseAdapter
        
        db = DatabaseAdapter()
        user = db.get_user(chat_id)
        
        if not user:
            return
        
        level = user.level
        daily_goal = db.get_daily_goal(level)
        today_count = db.get_today_activity_count(chat_id)
        remaining = daily_goal - today_count
        
        if remaining <= 0:
            message = f"🌅 Доброе утро, {first_name}!\n\n🎉 Ты уже выполнил дневную норму ({daily_goal} отжиманий)! Отличная работа!"
        else:
            message = f"🌅 Доброе утро, {first_name}!\n\n💪 Твоя цель на сегодня: {daily_goal} отжиманий\n📊 Уже выполнено: {today_count}\n🎯 Осталось: {remaining}\n\nНачни день с тренировки!"
        
        await bot.send_message(chat_id, message)
        logging.info(f"Отправлено утреннее напоминание пользователю {chat_id}")
        
    except Exception as e:
        logging.error(f"Ошибка при отправке утреннего напоминания пользователю {chat_id}: {e}")


async def send_afternoon_reminder(bot, chat_id, first_name):
    """Отправка дневного напоминания о тренировке."""
    try:
        from src.infrastructure.database import DatabaseAdapter
        
        db = DatabaseAdapter()
        user = db.get_user(chat_id)
        
        if not user:
            return
        
        level = user.level
        daily_goal = db.get_daily_goal(level)
        today_count = db.get_today_activity_count(chat_id)
        remaining = daily_goal - today_count
        
        if remaining <= 0:
            message = f"☀️ Привет, {first_name}!\n\n🎉 Ты уже выполнил дневную норму! Можешь отдохнуть или сделать дополнительные отжимания для укрепления!"
        else:
            message = f"☀️ Привет, {first_name}!\n\n💪 Не забудь про тренировку!\n📊 Прогресс: {today_count}/{daily_goal}\n🎯 Осталось: {remaining}\n\nСделай перерыв и выполни часть отжиманий!"
        
        await bot.send_message(chat_id, message)
        logging.info(f"Отправлено дневное напоминание пользователю {chat_id}")
        
    except Exception as e:
        logging.error(f"Ошибка при отправке дневного напоминания пользователю {chat_id}: {e}")


async def send_evening_reminder(bot, chat_id, first_name):
    """Отправка вечернего напоминания о тренировке."""
    try:
        from src.infrastructure.database import DatabaseAdapter
        
        db = DatabaseAdapter()
        user = db.get_user(chat_id)
        
        if not user:
            return
        
        level = user.level
        daily_goal = db.get_daily_goal(level)
        today_count = db.get_today_activity_count(chat_id)
        remaining = daily_goal - today_count
        
        if remaining <= 0:
            message = f"🌙 Добрый вечер, {first_name}!\n\n🎉 Отличная работа! Ты выполнил дневную норму {daily_goal} отжиманий!\n\nСпокойной ночи и до завтра!"
        else:
            message = f"🌙 Добрый вечер, {first_name}!\n\n⚠️ Не забудь про тренировку!\n📊 Прогресс: {today_count}/{daily_goal}\n🎯 Осталось: {remaining}\n\nСделай финальный рывок и выполни оставшиеся отжимания!"
        
        await bot.send_message(chat_id, message)
        logging.info(f"Отправлено вечернее напоминание пользователю {chat_id}")
        
    except Exception as e:
        logging.error(f"Ошибка при отправке вечернего напоминания пользователю {chat_id}: {e}")


async def send_level_up_notification(bot, chat_id, first_name, new_level, new_goal):
    """Отправка уведомления о повышении уровня."""
    try:
        level_names = {
            1: "Новичок",
            2: "Ученик", 
            3: "Подмастерье",
            4: "Мастер",
            5: "Эксперт",
            6: "Легенда"
        }
        
        message = f"🎊 Поздравляем, {first_name}!\n\n"
        message += f"🏆 Ты достиг нового уровня!\n"
        message += f"📈 Уровень: {new_level} ({level_names.get(new_level, 'Неизвестный')})\n"
        message += f"🎯 Новая цель: {new_goal} отжиманий в день\n\n"
        message += f"Продолжай в том же духе! Ты становишься сильнее!"
        
        await bot.send_message(chat_id, message)
        logging.info(f"Отправлено уведомление о повышении уровня пользователю {chat_id}")
        
    except Exception as e:
        logging.error(f"Ошибка при отправке уведомления о повышении уровня пользователю {chat_id}: {e}")


async def send_weekly_progress_report(bot, chat_id, first_name):
    """Отправка еженедельного отчета о прогрессе."""
    try:
        from src.infrastructure.database import DatabaseAdapter
        
        db = DatabaseAdapter()
        user = db.get_user(chat_id)
        
        if not user:
            return
        
        # Получаем статистику пользователя
        stats = db.get_user_stats(chat_id)
        
        if not stats:
            return
        
        # Формируем отчет
        message = f"📊 Еженедельный отчет, {first_name}!\n\n"
        message += f"📈 Уровень: {user.level}\n"
        message += f"🎯 Дневная цель: {db.get_daily_goal(user.level)} отжиманий\n"
        message += f"📅 Дней тренировки: {stats.days_count}\n"
        message += f"💪 Всего отжиманий: {stats.total_pushups}\n\n"
        
        if stats.days_count >= 7:
            message += "🎉 Отличная неделя! Ты тренировался каждый день!"
        elif stats.days_count >= 5:
            message += "👍 Хорошая неделя! Продолжай в том же духе!"
        else:
            message += "💪 На следующей неделе постарайся тренироваться чаще!"
        
        await bot.send_message(chat_id, message)
        logging.info(f"Отправлен еженедельный отчет о прогрессе пользователю {chat_id}")
        
    except Exception as e:
        logging.error(f"Ошибка при отправке еженедельного отчета о прогрессе пользователю {chat_id}: {e}") 