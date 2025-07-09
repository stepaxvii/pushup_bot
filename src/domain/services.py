"""
Domain services - business logic.
"""
from random import randint
from datetime import date
from typing import Optional

from src.domain.entities import User, Task


class TaskService:
    """Service for task generation and management."""
    
    @staticmethod
    def generate_task(user: User) -> Task:
        """Generate a new task for user based on their level."""
        pushups_count = TaskService._random_pushups(user.level)
        
        return Task(
            user_id=user.id,
            pushups_count=pushups_count,
            level=user.level,
            date=date.today()
        )
    
    @staticmethod
    def _random_pushups(level: int) -> int:
        """Generate random pushups count based on level."""
        levels = {
            1: (5, 15),    # Начинающий
            2: (10, 25),   # Новичок
            3: (15, 35),   # Средний
            4: (20, 45),   # Продвинутый
            5: (25, 60),   # Эксперт
            6: (30, 80)    # Мастер
        }
        
        if level not in levels:
            level = 1
        
        min_pushups, max_pushups = levels[level]
        return randint(min_pushups, max_pushups)


class UserService:
    """Service for user management."""
    
    @staticmethod
    def get_user_level_name(level: int) -> str:
        """Get user level name."""
        levels = {
            1: "Начинающий",
            2: "Новичок", 
            3: "Средний",
            4: "Продвинутый",
            5: "Эксперт",
            6: "Мастер"
        }
        return levels.get(level, "Неизвестный")
    
    @staticmethod
    def is_valid_level(level: int) -> bool:
        """Check if level is valid."""
        return 1 <= level <= 6


class AchievementService:
    """Service for achievements and rewards."""
    
    @staticmethod
    def get_achievement_message(days_count: int) -> Optional[str]:
        """Get achievement message for days count."""
        rewards = {
            7: "🎉 Неделя тренировок! Ты на правильном пути!",
            14: "🏆 Две недели! Ты формируешь привычку!",
            30: "👑 Месяц тренировок! Ты настоящий чемпион!",
            50: "💎 50 дней! Ты железный человек!",
            100: "🌟 100 дней! Ты легенда!"
        }
        
        return rewards.get(days_count)
    
    @staticmethod
    def get_motivational_message() -> str:
        """Get random motivational message."""
        messages = [
            "💪 Ты становишься сильнее с каждым днем!",
            "🔥 Твоя сила в регулярности!",
            "🏆 Каждый отжимание приближает тебя к цели!",
            "⭐ Ты делаешь это правильно!",
            "🚀 Твой прогресс впечатляет!",
            "💎 Ты настоящий боец!",
            "🌟 Твоя дисциплина достойна уважения!",
            "⚡ Ты заряжаешь энергией всех вокруг!"
        ]
        
        return messages[randint(0, len(messages) - 1)] 