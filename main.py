#!/usr/bin/env python3
"""
Telegram бот для отслеживания отжиманий.
"""
import asyncio
import logging
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command

from src.infrastructure.database import DatabaseAdapter
from src.application.use_cases import UserUseCase, TaskUseCase, StatsUseCase, AchievementUseCase
from src.presentation.handlers import MessageHandlers

# Загружаем переменные окружения
load_dotenv()

# Конфигурация
TOKEN_BOT = os.getenv('TOKEN_BOT')
if not TOKEN_BOT:
    raise ValueError("TOKEN_BOT не найден в переменных окружения!")

# Настройка логирования
logging.basicConfig(
    filename='bot_pushups.log',
    filemode='a',
    encoding='utf-8',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)


class BotApplication:
    """Основное приложение бота с чистой архитектурой."""
    
    def __init__(self):
        # Слой инфраструктуры
        self.db = DatabaseAdapter()
        
        # Слой приложения
        self.user_use_case = UserUseCase(self.db)
        self.task_use_case = TaskUseCase(self.db)
        self.stats_use_case = StatsUseCase(self.db)
        self.achievement_use_case = AchievementUseCase(self.db)
        
        # Слой представления
        self.handlers = MessageHandlers(
            self.user_use_case,
            self.task_use_case,
            self.stats_use_case,
            self.achievement_use_case
        )
        
        # Настройка бота
        if not TOKEN_BOT:
            raise ValueError("TOKEN_BOT обязателен")
        self.bot = Bot(token=TOKEN_BOT)
        self.dp = Dispatcher()
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Настройка обработчиков сообщений."""
        # Обработчики команд
        self.dp.message.register(self.handlers.start_handler, Command("start"))
        
        # Обработчики кнопок
        self.dp.message.register(self.handlers.new_task_handler, F.text == "🏋️‍♂️ Новое задание")
        self.dp.message.register(self.handlers.stats_handler, F.text == "📊 Моя статистика")
        self.dp.message.register(self.handlers.help_handler, F.text == "❓ Помощь")
        self.dp.message.register(self.handlers.settings_handler, F.text == "🎯 Настройки")
        
        # Обработчики callback-запросов
        self.dp.callback_query.register(self.handlers.done_callback_handler, F.data.startswith("done_"))
        self.dp.callback_query.register(self.handlers.custom_count_callback_handler, F.data == "custom_count")
        self.dp.callback_query.register(self.handlers.skip_callback_handler, F.data == "skip")
        self.dp.callback_query.register(self.handlers.set_level_callback_handler, F.data.startswith("set_level_"))
        self.dp.callback_query.register(self.handlers.back_to_main_callback_handler, F.data == "back_to_main")
        self.dp.callback_query.register(self.handlers.detailed_stats_callback_handler, F.data == "detailed_stats")  # type: ignore
        
        # Обработчик текста (ловит всё остальное)
        self.dp.message.register(self.handlers.text_handler)
    
    async def start(self):
        """Запуск бота."""
        logging.info("Запуск бота с чистой архитектурой...")
        try:
            await self.dp.start_polling(self.bot)
        except Exception as error:
            logging.error(f'Ошибка бота: {error}')
            raise


async def main():
    """Главная функция."""
    app = BotApplication()
    await app.start()


if __name__ == '__main__':
    asyncio.run(main()) 