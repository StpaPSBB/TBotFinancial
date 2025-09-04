"""Inline клавиатура для бота."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def edit_delete_inline_kb(transaction_id: str) -> InlineKeyboardMarkup:
    """Создает inline-клавиатуру для конкретной траты с кнопкой 'Удалить' и 'Изменить'."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Изменить", callback_data=f"edit_{transaction_id}"),
         InlineKeyboardButton(text="Удалить", callback_data=f"delete_{transaction_id}")]
    ])
    return keyboard


def date_inline_kb() -> InlineKeyboardMarkup:
    """Создает inline-клавиатуру для выбора даты траты."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Сегодня", callback_data=f"today"),
         InlineKeyboardButton(text="Другая дата", callback_data=f"another_date")]
    ])
    return keyboard