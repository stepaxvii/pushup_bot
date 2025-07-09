"""
Обработчики сообщений для Telegram бота.
"""
import logging
from typing import Optional

from aiogram import types, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery

from src.application.use_cases import UserUseCase, TaskUseCase, StatsUseCase, AchievementUseCase
from src.presentation.keyboards import (
    create_main_keyboard, 
    create_task_keyboard, 
    create_stats_keyboard, 
    create_settings_keyboard
)
from src.presentation.messages import *


class MessageHandlers:
    """Обработчики сообщений для бота."""
    
    def __init__(self, user_use_case: UserUseCase, task_use_case: TaskUseCase, 
                 stats_use_case: StatsUseCase, achievement_use_case: AchievementUseCase):
        self.user_use_case = user_use_case
        self.task_use_case = task_use_case
        self.stats_use_case = stats_use_case
        self.achievement_use_case = achievement_use_case
    
    async def start_handler(self, message: types.Message) -> None:
        """Обработка команды /start."""
        chat_id = message.chat.id
        first_name = message.chat.first_name or "Пользователь"
        
        # Регистрируем пользователя
        user = self.user_use_case.register_user(chat_id, first_name)
        
        if user:
            await message.answer(
                text=get_welcome_message(first_name),
                reply_markup=create_main_keyboard()
            )
        else:
            await message.answer(get_error_message())
    
    async def new_task_handler(self, message: types.Message) -> None:
        """Обработка кнопки нового задания."""
        try:
            chat_id = message.chat.id
            first_name = message.chat.first_name or "Пользователь"
            
            # Создаём задание (для тестирования - разрешаем несколько заданий в день)
            task = self.task_use_case.create_task(chat_id)
            
            if task:
                await message.answer(
                    text=get_task_message(first_name, task),
                    reply_markup=create_task_keyboard(task.pushups_count)
                )
            else:
                await message.answer(get_error_message())
        except Exception as e:
            logging.error(f"Ошибка в new_task_handler: {e}")
            await message.answer(get_error_message())
    
    async def stats_handler(self, message: types.Message) -> None:
        """Обработка кнопки статистики."""
        try:
            chat_id = message.chat.id
            first_name = message.chat.first_name or "Пользователь"
            
            stats = self.stats_use_case.get_user_stats(chat_id)
            
            if stats:
                await message.answer(
                    text=get_stats_message(stats),
                    reply_markup=create_stats_keyboard()
                )
            else:
                await message.answer(
                    get_no_stats_message(first_name),
                    reply_markup=create_main_keyboard()
                )
        except Exception as e:
            logging.error(f"Ошибка в stats_handler: {e}")
            await message.answer(get_error_message())
    
    async def help_handler(self, message: types.Message) -> None:
        """Обработка кнопки помощи."""
        try:
            await message.answer(
                text=get_help_message(),
                reply_markup=create_main_keyboard()
            )
        except Exception as e:
            logging.error(f"Ошибка в help_handler: {e}")
            await message.answer(get_error_message())
    
    async def settings_handler(self, message: types.Message) -> None:
        """Обработка кнопки настроек."""
        try:
            chat_id = message.chat.id
            first_name = message.chat.first_name or "Пользователь"
            
            user = self.user_use_case.get_user(chat_id)
            
            if user:
                await message.answer(
                    text=get_settings_message(first_name, user.level),
                    reply_markup=create_settings_keyboard(user.level)
                )
            else:
                await message.answer(get_error_message())
        except Exception as e:
            logging.error(f"Ошибка в settings_handler: {e}")
            await message.answer(get_error_message())
    
    async def done_callback_handler(self, callback: CallbackQuery) -> None:
        """Обработка callback для выполнения задания."""
        if not callback.message:
            await callback.answer("❌ Ошибка: сообщение не найдено")
            return
        
        chat_id = callback.message.chat.id
        first_name = callback.from_user.first_name or "Пользователь"
        
        if not callback.data:
            await callback.answer("❌ Ошибка: данные не найдены")
            return
        
        try:
            pushups_count = int(callback.data.split('_')[1])
        except (ValueError, IndexError):
            await callback.answer("❌ Ошибка при обработке данных")
            return
        
        # Выполняем задание
        if self.task_use_case.complete_task(chat_id, pushups_count):
            response = get_task_completed_message(first_name, pushups_count)
            
            # Проверяем достижения
            achievement = self.achievement_use_case.check_achievements(chat_id)
            if achievement:
                response += f"\n\n{achievement}"
            
            try:
                await callback.message.edit_text(response)  # type: ignore
            except Exception:
                await callback.message.answer(response)
            
            await callback.message.answer(
                "🏋️‍♂️ Главное меню\n\nВыбери действие:",
                reply_markup=create_main_keyboard()
            )
            await callback.answer("✅ Задание выполнено!")
        else:
            await callback.answer("❌ Ошибка при сохранении результата")
    
    async def custom_count_callback_handler(self, callback: CallbackQuery) -> None:
        """Обработка callback для ввода своего количества."""
        if not callback.message:
            await callback.answer("❌ Ошибка: сообщение не найдено")
            return
        
        try:
            await callback.message.edit_text(  # type: ignore
                "✏️ Введи количество отжиманий, которое ты выполнил:"
            )
        except Exception:
            await callback.message.answer(
                "✏️ Введи количество отжиманий, которое ты выполнил:"
            )
        
        await callback.answer()
    
    async def skip_callback_handler(self, callback: CallbackQuery) -> None:
        """Обработка callback для пропуска задания."""
        if not callback.message:
            await callback.answer("❌ Ошибка: сообщение не найдено")
            return
        
        chat_id = callback.message.chat.id
        first_name = callback.from_user.first_name
        
        # Пропускаем задание
        if self.task_use_case.skip_task(chat_id):
            response = get_task_skipped_message(first_name)
            
            try:
                await callback.message.edit_text(response)  # type: ignore
            except Exception:
                await callback.message.answer(response)
            
            await callback.message.answer(
                "🏋️‍♂️ Главное меню\n\nВыбери действие:",
                reply_markup=create_main_keyboard()
            )
            await callback.answer("⏭️ День пропущен")
        else:
            await callback.answer("❌ Ошибка при сохранении результата")
    
    async def set_level_callback_handler(self, callback: CallbackQuery) -> None:
        """Обработка callback для установки уровня."""
        if not callback.message:
            await callback.answer("❌ Ошибка: сообщение не найдено")
            return
        
        chat_id = callback.message.chat.id
        first_name = callback.from_user.first_name
        
        if not callback.data:
            await callback.answer("❌ Ошибка: данные не найдены")
            return
        
        try:
            new_level = int(callback.data.split('_')[2])
        except (ValueError, IndexError):
            await callback.answer("❌ Ошибка при обработке данных")
            return
        
        # Update level
        if self.user_use_case.update_user_level(chat_id, new_level):
            response = get_level_updated_message(first_name, new_level)
            
            try:
                await callback.message.edit_text(response)  # type: ignore
            except Exception:
                await callback.message.answer(response)
            
            await callback.message.answer(
                "🏋️‍♂️ Главное меню\n\nВыбери действие:",
                reply_markup=create_main_keyboard()
            )
            await callback.answer(f"✅ Уровень изменен на {new_level}")
        else:
            await callback.answer("❌ Ошибка при изменении уровня")
    
    async def back_to_main_callback_handler(self, callback: CallbackQuery) -> None:
        """Handle back to main callback."""
        if not callback.message:
            await callback.answer("❌ Ошибка: сообщение не найдено")
            return
        
        try:
            await callback.message.edit_text("🏋️‍♂️ Главное меню\n\nВыбери действие:")  # type: ignore
        except Exception:
            pass
        
        await callback.message.answer(
            "🏋️‍♂️ Главное меню\n\nВыбери действие:",
            reply_markup=create_main_keyboard()
        )

    async def detailed_stats_callback_handler(self, callback: CallbackQuery) -> None:
        """Handle detailed statistics callback."""
        if not callback.message:
            await callback.answer("❌ Ошибка: сообщение не найдено")
            return
        
        chat_id = callback.message.chat.id
        first_name = callback.from_user.first_name or "Пользователь"
        
        # Получаем детальную статистику
        from src.infrastructure.database import DatabaseAdapter
        db = DatabaseAdapter()
        detailed_stats = db.get_detailed_stats(chat_id)
        
        if detailed_stats:
            from src.presentation.messages import get_detailed_stats_message
            response = get_detailed_stats_message(first_name, detailed_stats)
            
            try:
                await callback.message.edit_text(response)  # type: ignore
            except Exception:
                await callback.message.answer(response)
            
            await callback.answer("📊 Детальная статистика загружена!")
        else:
            await callback.answer("❌ Ошибка при загрузке статистики")
    
    async def text_handler(self, message: types.Message) -> None:
        """Handle text messages."""
        text = message.text
        
        if not text:
            await message.answer(
                get_unknown_command_message(),
                reply_markup=create_main_keyboard()
            )
            return
        
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['привет', 'hello', 'hi']):
            await message.answer(
                get_greeting_message(),
                reply_markup=create_main_keyboard()
            )
        elif any(word in text_lower for word in ['спасибо', 'thanks', 'thank']):
            await message.answer(
                get_thanks_message(),
                reply_markup=create_main_keyboard()
            )
        else:
            # Check if message is a number
            try:
                number = int(text)
                if 0 <= number <= 1000:  # Reasonable limits
                    await self._process_custom_count(message, number)
                    return
            except ValueError:
                pass
            
            await message.answer(
                get_unknown_command_message(),
                reply_markup=create_main_keyboard()
            )
    
    async def _process_custom_count(self, message: types.Message, pushups_count: int) -> None:
        """Process custom pushups count."""
        chat_id = message.chat.id
        first_name = message.chat.first_name
        
        if pushups_count < 0:
            await message.answer(
                get_negative_number_message(),
                reply_markup=create_main_keyboard()
            )
            return
        
        # Complete task
        if self.task_use_case.complete_task(chat_id, pushups_count):
            response = get_task_completed_message(first_name or "Пользователь", pushups_count)
            
            # Check achievements
            achievement = self.achievement_use_case.check_achievements(chat_id)
            if achievement:
                response += f"\n\n{achievement}"
            
            await message.answer(
                response,
                reply_markup=create_main_keyboard()
            )
        else:
            await message.answer(
                get_error_message(),
                reply_markup=create_main_keyboard()
            ) 