from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


main_reply_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Добавить сегодняшнюю трату"),
     KeyboardButton(text="Показать траты за месяц")]
],
                                    resize_keyboard=True,
                                    input_field_placeholder="Воспользуйтесь кнопками ниже."
)