import asyncio
from datetime import datetime
import logging
import os
from dotenv import load_dotenv
from src.infrastructure.tasks import send_morning_reminder, send_afternoon_reminder, send_evening_reminder, send_weekly_progress_report
from src.infrastructure.database import DatabaseAdapter

load_dotenv()

logging.basicConfig(
    filename='scheduler.log',
    filemode='a',
    encoding='utf-8',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)

def get_active_users():
    """Получение активных пользователей из базы данных."""
    try:
        db = DatabaseAdapter()
        users = db.get_all_active_users()
        return [{'user_id': user[0], 'name': user[1]} for user in users]
        
    except Exception as e:
        logging.error(f"Ошибка при получении активных пользователей: {e}")
        return []

async def schedule_morning_reminders():
    """Отправка утренних напоминаний (8:00)."""
    users = get_active_users()
    if not users:
        logging.info("Нет активных пользователей для отправки утренних напоминаний")
        return
    
    for user in users:
        send_morning_reminder.delay(user['user_id'])
    logging.info(f"Отправлены утренние напоминания для {len(users)} пользователей")

async def schedule_afternoon_reminders():
    """Отправка дневных напоминаний (14:00)."""
    users = get_active_users()
    if not users:
        logging.info("Нет активных пользователей для отправки дневных напоминаний")
        return
    
    for user in users:
        send_afternoon_reminder.delay(user['user_id'])
    logging.info(f"Отправлены дневные напоминания для {len(users)} пользователей")

async def schedule_evening_reminders():
    """Отправка вечерних напоминаний (20:00)."""
    users = get_active_users()
    if not users:
        logging.info("Нет активных пользователей для отправки вечерних напоминаний")
        return
    
    for user in users:
        send_evening_reminder.delay(user['user_id'])
    logging.info(f"Отправлены вечерние напоминания для {len(users)} пользователей")

async def schedule_weekly_reports():
    """Отправка еженедельных отчётов (воскресенье 18:00)."""
    users = get_active_users()
    if not users:
        logging.info("Нет активных пользователей для отправки еженедельных отчётов")
        return
    
    for user in users:
        send_weekly_progress_report.delay(user['user_id'])
    logging.info(f"Отправлены еженедельные отчёты для {len(users)} пользователей")

async def main():
    """Основная функция планировщика."""
    logging.info("Планировщик запущен - уведомления трижды в день")
    print("⏰ Планировщик запущен!")
    print("📅 Расписание уведомлений:")
    print("   🌅 8:00 - Утренние напоминания")
    print("   ☀️ 14:00 - Дневные напоминания") 
    print("   🌙 20:00 - Вечерние напоминания")
    print("   📊 Воскресенье 18:00 - Еженедельные отчёты")
    print("=" * 50)
    
    while True:
        now = datetime.now()
        
        # Утренние напоминания в 8:00
        if now.hour == 8 and now.minute == 0:
            await schedule_morning_reminders()
        
        # Дневные напоминания в 14:00
        if now.hour == 14 and now.minute == 0:
            await schedule_afternoon_reminders()
        
        # Вечерние напоминания в 20:00
        if now.hour == 20 and now.minute == 0:
            await schedule_evening_reminders()
        
        # Еженедельные отчёты в воскресенье в 18:00
        if now.weekday() == 6 and now.hour == 18 and now.minute == 0:
            await schedule_weekly_reports()
        
        await asyncio.sleep(60)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Остановлено пользователем") 