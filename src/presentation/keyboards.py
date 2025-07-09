"""
Keyboard layouts for Telegram bot.
"""
from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def create_main_keyboard() -> ReplyKeyboardMarkup:
    """Create main keyboard."""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="🏋️‍♂️ Новое задание"))
    builder.add(KeyboardButton(text="📊 Моя статистика"))
    builder.add(KeyboardButton(text="❓ Помощь"))
    builder.add(KeyboardButton(text="🎯 Настройки"))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def create_task_keyboard(pushups_count: int) -> InlineKeyboardMarkup:
    """Create keyboard for task completion."""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text=f"✅ Выполнил ({pushups_count})", 
        callback_data=f"done_{pushups_count}"
    ))
    builder.add(InlineKeyboardButton(
        text="✏️ Другое количество", 
        callback_data="custom_count"
    ))
    builder.add(InlineKeyboardButton(
        text="⏭️ Пропустить", 
        callback_data="skip"
    ))
    builder.adjust(2, 1)
    return builder.as_markup()


def create_stats_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for statistics."""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="📈 Детальная статистика", 
        callback_data="detailed_stats"
    ))
    builder.add(InlineKeyboardButton(
        text="🏆 Достижения", 
        callback_data="achievements"
    ))
    builder.add(InlineKeyboardButton(
        text="📅 История", 
        callback_data="history"
    ))
    builder.add(InlineKeyboardButton(
        text="🔙 Назад", 
        callback_data="back_to_main"
    ))
    builder.adjust(2)
    return builder.as_markup()


def create_settings_keyboard(current_level: int) -> InlineKeyboardMarkup:
    """Create keyboard for settings."""
    builder = InlineKeyboardBuilder()
    for i in range(1, 7):
        emoji = "✅" if i == current_level else f"{i}️⃣"
        builder.add(InlineKeyboardButton(
            text=f"{emoji} Уровень {i}", 
            callback_data=f"set_level_{i}"
        ))
    builder.adjust(3, 3)
    return builder.as_markup() 