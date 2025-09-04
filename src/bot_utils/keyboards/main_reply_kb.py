"""Reply клавиатура для бота."""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


reply_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Добавить трату")],
    [KeyboardButton(text="Показать траты за месяц"),
     KeyboardButton(text="Показать траты за сегодня")]
],
                                    resize_keyboard=True,
                                    input_field_placeholder="Воспользуйтесь кнопками ниже."
)