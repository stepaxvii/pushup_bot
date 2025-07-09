"""
Адаптер базы данных - слой инфраструктуры.
"""
import sqlite3
import logging
import os
from datetime import datetime, date
from typing import Optional, List, Tuple

from src.domain.entities import User, DailyActivity, UserStats


class DatabaseAdapter:
    """Адаптер базы данных для SQLite."""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            self.db_path = os.getenv('DB_PATH', 'users.db')
        else:
            self.db_path = db_path
        
        # Создаём директорию для базы данных, если её нет
        db_dir = os.path.dirname(self.db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            
        self._init_database()
    
    def _init_database(self):
        """Инициализация таблиц базы данных."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Таблица пользователей
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER UNIQUE NOT NULL,
                first_name TEXT NOT NULL,
                level INTEGER DEFAULT 1,
                days INTEGER DEFAULT 0,
                total_count INTEGER DEFAULT 0,
                last_activity_date DATE,
                consecutive_days INTEGER DEFAULT 0,
                daily_goal INTEGER DEFAULT 30
            )
        """)
        
        # Таблица ежедневной активности
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                activity_date DATE NOT NULL,
                pushups_count INTEGER NOT NULL,
                completed BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Получение соединения с базой данных."""
        return sqlite3.connect(self.db_path)
    
    def save_user(self, chat_id: int, first_name: str) -> Optional[User]:
        """Сохранение или обновление пользователя."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Проверяем, существует ли пользователь
            cursor.execute(
                "SELECT * FROM users WHERE chat_id = ?",
                (chat_id,)
            )
            existing_user = cursor.fetchone()
            
            if existing_user:
                # Обновляем существующего пользователя
                cursor.execute("""
                    UPDATE users 
                    SET first_name = ?, last_activity_date = CURRENT_DATE
                    WHERE chat_id = ?
                """, (first_name, chat_id))
                
                user_data = (existing_user[0], chat_id, first_name, 
                           existing_user[3], existing_user[4], 
                           existing_user[5], existing_user[6] if existing_user[6] else None)
            else:
                # Создаём нового пользователя
                cursor.execute("""
                    INSERT INTO users (chat_id, first_name, level, days, total_count, last_activity_date)
                    VALUES (?, ?, 1, 0, 0, CURRENT_DATE)
                """, (chat_id, first_name))
                
                user_id = cursor.lastrowid
                user_data = (user_id, chat_id, first_name, 1, 0, 0, date.today())
            
            conn.commit()
            conn.close()
            
            if user_data[0] is not None:  # Убеждаемся, что id не None
                return User(*user_data)  # type: ignore
            return None
            
        except Exception as e:
            logging.error(f"Ошибка сохранения пользователя: {e}")
            return None
    
    def get_user(self, chat_id: int) -> Optional[User]:
        """Получение пользователя по chat_id."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM users WHERE chat_id = ?",
                (chat_id,)
            )
            user_data = cursor.fetchone()
            conn.close()
            
            if user_data:
                return User(*user_data)
            return None
            
        except Exception as e:
            logging.error(f"Ошибка получения пользователя: {e}")
            return None
    
    def save_daily_activity(self, user_id: int, pushups_count: int) -> bool:
        """Сохранение ежедневной активности."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Получаем chat_id пользователя
            cursor.execute("SELECT chat_id FROM users WHERE id = ?", (user_id,))
            user_result = cursor.fetchone()
            if not user_result:
                conn.close()
                return False
            
            chat_id = user_result[0]
            
            # Проверяем, существует ли активность на сегодня
            cursor.execute("""
                SELECT id FROM daily_activity 
                WHERE user_id = ? AND activity_date = CURRENT_DATE
            """, (user_id,))
            
            existing_activity = cursor.fetchone()
            
            if existing_activity:
                # Обновляем существующую активность - суммируем количество
                cursor.execute("""
                    UPDATE daily_activity 
                    SET pushups_count = pushups_count + ?, completed = TRUE
                    WHERE id = ?
                """, (pushups_count, existing_activity[0]))
            else:
                # Создаём новую активность
                cursor.execute("""
                    INSERT INTO daily_activity (user_id, activity_date, pushups_count, completed)
                    VALUES (?, CURRENT_DATE, ?, TRUE)
                """, (user_id, pushups_count))
            
            # Обновляем статистику пользователя
            # Если это новая активность, добавляем к общему счету
            if not existing_activity:
                cursor.execute("""
                    UPDATE users 
                    SET total_count = total_count + ?,
                        last_activity_date = CURRENT_DATE
                    WHERE id = ?
                """, (pushups_count, user_id))
            else:
                # Если обновляем существующую активность, обновляем только дату
                cursor.execute("""
                    UPDATE users 
                    SET last_activity_date = CURRENT_DATE
                    WHERE id = ?
                """, (user_id,))
            
            # Обновляем дни подряд
            self.update_consecutive_days(chat_id)
            
            # Проверяем повышение уровня
            self.check_level_up(chat_id)
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logging.error(f"Ошибка сохранения ежедневной активности: {e}")
            return False
    
    def get_user_stats(self, chat_id: int) -> Optional[UserStats]:
        """Get user statistics."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get user data
            cursor.execute(
                "SELECT * FROM users WHERE chat_id = ?",
                (chat_id,)
            )
            user_data = cursor.fetchone()
            
            if not user_data:
                conn.close()
                return None
            
            user = User(*user_data)
            
            # Get statistics
            cursor.execute("""
                SELECT COUNT(*), SUM(pushups_count), MAX(activity_date)
                FROM daily_activity 
                WHERE user_id = ? AND completed = TRUE
            """, (user.id,))
            
            stats_data = cursor.fetchone()
            conn.close()
            
            days_count = stats_data[0] or 0
            total_pushups = stats_data[1] or 0
            last_activity = stats_data[2]
            
            stats = {
                'days_count': days_count,
                'total_pushups': total_pushups,
                'last_activity': last_activity
            }
            
            return UserStats(
                user_data=user,
                stats=stats,
                days_count=days_count,
                total_pushups=total_pushups,
                last_activity=last_activity
            )
            
        except Exception as e:
            logging.error(f"Error getting user stats: {e}")
            return None
    
    def check_today_activity(self, chat_id: int) -> bool:
        """Check if user completed activity today."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT SUM(pushups_count) FROM daily_activity da
                JOIN users u ON da.user_id = u.id
                WHERE u.chat_id = ? AND da.activity_date = CURRENT_DATE AND da.completed = TRUE
            """, (chat_id,))
            
            total_count = cursor.fetchone()[0] or 0
            conn.close()
            
            return total_count > 0
            
        except Exception as e:
            logging.error(f"Error checking today activity: {e}")
            return False
    
    def update_user_level(self, chat_id: int, new_level: int) -> bool:
        """Update user level."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users SET level = ? WHERE chat_id = ?
            """, (new_level, chat_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logging.error(f"Error updating user level: {e}")
            return False
    
    def get_all_active_users(self) -> List[Tuple[int, str]]:
        """Get all active users."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT chat_id, first_name 
                FROM users 
                WHERE last_activity_date IS NOT NULL
            """)
            
            users = cursor.fetchall()
            conn.close()
            
            return users
            
        except Exception as e:
            logging.error(f"Error getting active users: {e}")
            return []

    def get_daily_goal(self, level: int) -> int:
        """Получение ежедневной цели по уровню."""
        goals = {
            1: 30,   # Уровень 1: 30 отжиманий в день
            2: 45,   # Уровень 2: 45 отжиманий в день
            3: 60,   # Уровень 3: 60 отжиманий в день
            4: 75,   # Уровень 4: 75 отжиманий в день
            5: 90,   # Уровень 5: 90 отжиманий в день
            6: 100   # Уровень 6: 100 отжиманий в день
        }
        return goals.get(level, 30)

    def get_today_activity_count(self, chat_id: int) -> int:
        """Получение количества отжиманий за сегодня."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT SUM(pushups_count) 
                FROM daily_activity 
                WHERE user_id = (SELECT id FROM users WHERE chat_id = ?) 
                AND activity_date = CURRENT_DATE
            """, (chat_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            return result[0] or 0
            
        except Exception as e:
            logging.error(f"Ошибка при получении активности за сегодня: {e}")
            return 0

    def get_detailed_stats(self, chat_id: int) -> dict:
        """Получение детальной статистики пользователя."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Получаем данные пользователя
            cursor.execute("SELECT * FROM users WHERE chat_id = ?", (chat_id,))
            user_data = cursor.fetchone()
            
            if not user_data:
                conn.close()
                return {}
            
            user_id = user_data[0]
            
            # Общая статистика
            cursor.execute("""
                SELECT COUNT(*), SUM(pushups_count), MAX(activity_date), MIN(activity_date)
                FROM daily_activity 
                WHERE user_id = ? AND completed = TRUE
            """, (user_id,))
            
            stats_data = cursor.fetchone()
            
            # Статистика за неделю
            cursor.execute("""
                SELECT COUNT(*), SUM(pushups_count)
                FROM daily_activity 
                WHERE user_id = ? AND activity_date >= date('now', '-7 days') AND completed = TRUE
            """, (user_id,))
            
            week_stats = cursor.fetchone()
            
            # Статистика за месяц
            cursor.execute("""
                SELECT COUNT(*), SUM(pushups_count)
                FROM daily_activity 
                WHERE user_id = ? AND activity_date >= date('now', '-30 days') AND completed = TRUE
            """, (user_id,))
            
            month_stats = cursor.fetchone()
            
            # Среднее количество отжиманий в день
            cursor.execute("""
                SELECT AVG(pushups_count)
                FROM daily_activity 
                WHERE user_id = ? AND completed = TRUE
            """, (user_id,))
            
            avg_pushups = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                'total_days': stats_data[0] or 0,
                'total_pushups': stats_data[1] or 0,
                'first_activity': stats_data[3],
                'last_activity': stats_data[2],
                'week_days': week_stats[0] or 0,
                'week_pushups': week_stats[1] or 0,
                'month_days': month_stats[0] or 0,
                'month_pushups': month_stats[1] or 0,
                'avg_per_day': round(avg_pushups, 1),
                'current_level': user_data[3],
                'consecutive_days': user_data[7] or 0
            }
            
        except Exception as e:
            logging.error(f"Ошибка при получении детальной статистики: {e}")
            return {}

    def update_consecutive_days(self, chat_id: int) -> bool:
        """Обновление количества дней подряд."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Получаем информацию о пользователе
            cursor.execute("""
                SELECT consecutive_days, last_activity_date 
                FROM users 
                WHERE chat_id = ?
            """, (chat_id,))
            
            user_data = cursor.fetchone()
            if not user_data:
                conn.close()
                return False
            
            consecutive_days, last_activity_date = user_data
            
            # Проверяем, был ли вчера активность
            if last_activity_date:
                from datetime import date, timedelta
                yesterday = date.today() - timedelta(days=1)
                
                if last_activity_date == yesterday.isoformat():
                    # Вчера была активность - увеличиваем счетчик
                    new_consecutive_days = consecutive_days + 1
                else:
                    # Вчера не было активности - сбрасываем счетчик
                    new_consecutive_days = 1
            else:
                # Первая активность
                new_consecutive_days = 1
            
            # Обновляем счетчик дней подряд
            cursor.execute("""
                UPDATE users 
                SET consecutive_days = ?
                WHERE chat_id = ?
            """, (new_consecutive_days, chat_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logging.error(f"Ошибка при обновлении дней подряд: {e}")
            return False

    def check_level_up(self, chat_id: int) -> bool:
        """Проверка повышения уровня (7 дней подряд)."""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT level, consecutive_days 
                FROM users 
                WHERE chat_id = ?
            """, (chat_id,))
            
            user_data = cursor.fetchone()
            if not user_data:
                conn.close()
                return False
            
            level, consecutive_days = user_data
            
            # Проверяем, достиг ли пользователь 7 дней подряд
            if consecutive_days >= 7 and level < 6:
                new_level = level + 1
                new_goal = self.get_daily_goal(new_level)
                
                # Обновляем уровень и цель
                cursor.execute("""
                    UPDATE users 
                    SET level = ?, daily_goal = ?, consecutive_days = 0
                    WHERE chat_id = ?
                """, (new_level, new_goal, chat_id))
                
                conn.commit()
                conn.close()
                return True
            
            conn.close()
            return False
            
        except Exception as e:
            logging.error(f"Ошибка при проверке повышения уровня: {e}")
            return False 