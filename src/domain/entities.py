"""
Domain entities - core business objects.
"""
from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class User:
    """User entity."""
    id: int
    chat_id: int
    first_name: str
    level: int
    days: int
    total_count: int
    last_activity_date: Optional[date]
    consecutive_days: int
    daily_goal: int


@dataclass
class DailyActivity:
    """Daily activity entity."""
    id: int
    user_id: int
    activity_date: date
    pushups_count: int
    completed: bool
    created_at: date


@dataclass
class UserStats:
    """User statistics entity."""
    user_data: User
    stats: dict
    days_count: int
    total_pushups: int
    last_activity: Optional[str]


@dataclass
class Task:
    """Task entity."""
    user_id: int
    pushups_count: int
    level: int
    date: date 