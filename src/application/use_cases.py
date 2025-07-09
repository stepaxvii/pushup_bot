"""
Сценарии использования приложения - бизнес-операции.
"""
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
        user = self.db.get_user(chat_id)
        if not user:
            return None
        
        # Генерируем новое задание без проверки на уже выполненное
        # (для тестирования - разрешаем несколько заданий в день)
        task = TaskService.generate_task(user)
        
        # Не сохраняем задание в базу данных пока - только при выполнении
        # self.db.save_daily_activity(user.id, task.pushups_count)
        
        return task
    
    def complete_task(self, chat_id: int, pushups_count: int) -> bool:
        """Выполнение задания с пользовательским количеством отжиманий."""
        user = self.db.get_user(chat_id)
        if not user:
            return False
        
        return self.db.save_daily_activity(user.id, pushups_count)
    
    def skip_task(self, chat_id: int) -> bool:
        """Пропуск сегодняшнего задания."""
        user = self.db.get_user(chat_id)
        if not user:
            return False
        
        return self.db.save_daily_activity(user.id, 0)


class StatsUseCase:
    """Сценарии использования для статистики."""
    
    def __init__(self, db: DatabaseAdapter):
        self.db = db
    
    def get_user_stats(self, chat_id: int) -> Optional[UserStats]:
        """Получение статистики пользователя."""
        return self.db.get_user_stats(chat_id)
    
    def check_today_activity(self, chat_id: int) -> bool:
        """Проверка, выполнил ли пользователь активность сегодня."""
        return self.db.check_today_activity(chat_id)


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