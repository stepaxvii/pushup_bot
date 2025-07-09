"""
Сценарии использования приложения - бизнес-операции.
"""
import logging
from typing import Optional
from datetime import date

from src.domain.entities import User, Task, UserStats
from src.domain.services import TaskService, UserService, AchievementService
from src.infrastructure.database import DatabaseAdapter


class UserUseCase:
    """Сценарии использования для управления пользователями."""
    
    def __init__(self, db: DatabaseAdapter):
        self.db = db
    
    def register_user(self, chat_id: int, first_name: str) -> Optional[User]:
        """Регистрация или обновление пользователя."""
        return self.db.save_user(chat_id, first_name)
    
    def get_user(self, chat_id: int) -> Optional[User]:
        """Получение пользователя по chat_id."""
        return self.db.get_user(chat_id)
    
    def update_user_level(self, chat_id: int, new_level: int) -> bool:
        """Обновление уровня пользователя."""
        if not UserService.is_valid_level(new_level):
            return False
        return self.db.update_user_level(chat_id, new_level)


class TaskUseCase:
    """Сценарии использования для управления заданиями."""
    
    def __init__(self, db: DatabaseAdapter):
        self.db = db
    
    def create_task(self, chat_id: int) -> Optional[Task]:
        """Создание нового задания для пользователя."""
        try:
            user = self.db.get_user(chat_id)
            if not user:
                logging.error(f"Пользователь не найден для chat_id: {chat_id}")
                return None
            
            # Генерируем новое задание без проверки на уже выполненное
            # (для тестирования - разрешаем несколько заданий в день)
            task = TaskService.generate_task(user)
            logging.info(f"Создано задание для пользователя {chat_id}: {task.pushups_count} отжиманий")
            
            # Не сохраняем задание в базу данных пока - только при выполнении
            # self.db.save_daily_activity(user.id, task.pushups_count)
            
            return task
        except Exception as e:
            logging.error(f"Ошибка при создании задания для chat_id {chat_id}: {e}")
            return None
    
    def complete_task(self, chat_id: int, pushups_count: int) -> bool:
        """Выполнение задания с пользовательским количеством отжиманий."""
        try:
            user = self.db.get_user(chat_id)
            if not user:
                logging.error(f"Пользователь не найден для chat_id: {chat_id}")
                return False
            
            result = self.db.save_daily_activity(user.id, pushups_count)
            logging.info(f"Задание выполнено для пользователя {chat_id}: {pushups_count} отжиманий")
            return result
        except Exception as e:
            logging.error(f"Ошибка при выполнении задания для chat_id {chat_id}: {e}")
            return False
    
    def skip_task(self, chat_id: int) -> bool:
        """Пропуск сегодняшнего задания."""
        try:
            user = self.db.get_user(chat_id)
            if not user:
                logging.error(f"Пользователь не найден для chat_id: {chat_id}")
                return False
            
            result = self.db.save_daily_activity(user.id, 0)
            logging.info(f"Задание пропущено для пользователя {chat_id}")
            return result
        except Exception as e:
            logging.error(f"Ошибка при пропуске задания для chat_id {chat_id}: {e}")
            return False


class StatsUseCase:
    """Сценарии использования для статистики."""
    
    def __init__(self, db: DatabaseAdapter):
        self.db = db
    
    def get_user_stats(self, chat_id: int) -> Optional[UserStats]:
        """Получение статистики пользователя."""
        try:
            stats = self.db.get_user_stats(chat_id)
            if stats:
                logging.info(f"Получена статистика для пользователя {chat_id}")
            else:
                logging.warning(f"Статистика не найдена для пользователя {chat_id}")
            return stats
        except Exception as e:
            logging.error(f"Ошибка при получении статистики для chat_id {chat_id}: {e}")
            return None
    
    def check_today_activity(self, chat_id: int) -> bool:
        """Проверка, выполнил ли пользователь активность сегодня."""
        try:
            result = self.db.check_today_activity(chat_id)
            logging.info(f"Проверка активности для пользователя {chat_id}: {result}")
            return result
        except Exception as e:
            logging.error(f"Ошибка при проверке активности для chat_id {chat_id}: {e}")
            return False


class AchievementUseCase:
    """Сценарии использования для достижений."""
    
    def __init__(self, db: DatabaseAdapter):
        self.db = db
    
    def check_achievements(self, chat_id: int) -> Optional[str]:
        """Проверка и возврат сообщения о достижении."""
        stats = self.db.get_user_stats(chat_id)
        if not stats:
            return None
        
        return AchievementService.get_achievement_message(stats.days_count)
    
    def get_motivational_message(self) -> str:
        """Получение случайного мотивирующего сообщения."""
        return AchievementService.get_motivational_message() 