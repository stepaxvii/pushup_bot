import os
import asyncio
import logging
from dotenv import load_dotenv
from aiogram import Bot
from src.infrastructure.celery_app import celery_app
# Импортируем функции уведомлений
import notifications

load_dotenv()

TOKEN_BOT = os.getenv('TOKEN_BOT')
if not TOKEN_BOT:
    raise ValueError("TOKEN_BOT не найден в переменных окружения!")

@celery_app.task
def send_morning_reminder(user_id: int):
    """Отправка утреннего напоминания через Celery."""
    try:
        # Создаем новый экземпляр бота для каждой задачи
        bot = Bot(token=TOKEN_BOT or "")
        
        # Запускаем асинхронную функцию в синхронном контексте
        asyncio.run(notifications.send_morning_reminder(bot, user_id, "Пользователь"))
        
        logging.info(f"Отправлено утреннее напоминание пользователю {user_id}")
    except Exception as e:
        logging.error(f"Ошибка при отправке утреннего напоминания пользователю {user_id}: {e}")

@celery_app.task
def send_afternoon_reminder(user_id: int):
    """Отправка дневного напоминания через Celery."""
    try:
        # Создаем новый экземпляр бота для каждой задачи
        bot = Bot(token=TOKEN_BOT or "")
        
        # Запускаем асинхронную функцию в синхронном контексте
        asyncio.run(notifications.send_afternoon_reminder(bot, user_id, "Пользователь"))
        
        logging.info(f"Отправлено дневное напоминание пользователю {user_id}")
    except Exception as e:
        logging.error(f"Ошибка при отправке дневного напоминания пользователю {user_id}: {e}")

@celery_app.task
def send_evening_reminder(user_id: int):
    """Отправка вечернего напоминания через Celery."""
    try:
        # Создаем новый экземпляр бота для каждой задачи
        bot = Bot(token=TOKEN_BOT or "")
        
        # Запускаем асинхронную функцию в синхронном контексте
        asyncio.run(notifications.send_evening_reminder(bot, user_id, "Пользователь"))
        
        logging.info(f"Отправлено вечернее напоминание пользователю {user_id}")
    except Exception as e:
        logging.error(f"Ошибка при отправке вечернего напоминания пользователю {user_id}: {e}")

@celery_app.task
def send_weekly_progress_report(user_id: int):
    """Отправка еженедельного отчета через Celery."""
    try:
        # Создаем новый экземпляр бота для каждой задачи
        bot = Bot(token=TOKEN_BOT or "")
        
        # Запускаем асинхронную функцию в синхронном контексте
        asyncio.run(notifications.send_weekly_progress_report(bot, user_id, "Пользователь"))
        
        logging.info(f"Отправлен еженедельный отчет пользователю {user_id}")
    except Exception as e:
        logging.error(f"Ошибка при отправке еженедельного отчета пользователю {user_id}: {e}") 