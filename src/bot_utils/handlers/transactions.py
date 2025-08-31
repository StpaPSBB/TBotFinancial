"""Хендлеры для работы с транзакциями."""
import decimal
from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from src.database.services import create_transaction, get_month_transactions, get_month_transactions_price
from .states import NewTransaction

transactions_router = Router()


@transactions_router.message(F.text == "Показать траты за месяц")
async def cmd_show_month_transactions(message: Message):
    """
    Обрабатывает команду 'Показать траты за месяц'.
    Выводит траты за месяц и общую их стоимость.
    """
    user_id = message.from_user.id
    transactions = await get_month_transactions(user_telegram_id=user_id)
    total_price = await get_month_transactions_price(user_telegram_id=user_id)
    if transactions:    
        for i, transaction in enumerate(transactions, 1):
            idx = i
            name = transaction["name"]
            price = transaction["price"]
            date = transaction["created_at"]
            await message.answer(f"{idx}. Трата: {name}. Цена: {price} рублей. Дата: {date}")
        await message.answer(f"Общие траты за месяц - {total_price:.2f} рублей.")
    else:
        await message.answer("Вы пока не добавляли никаких трат в этом месяце.")


@transactions_router.message(F.text == "Добавить сегодняшнюю трату")
async def start_adding_transaction(message: Message, state: FSMContext):
    """
    Начинает процесс добавления новой траты.
    Устанавливает состояние для ввода названия траты.
    """
    await state.set_state(NewTransaction.name)
    await message.answer("Введите название траты.")
    


@transactions_router.message(NewTransaction.name)
async def process_transaction_name(message: Message, state: FSMContext):
    """Обрабатывает ввод названия траты и запрашивает цену."""
    await state.update_data(name=message.text)
    await state.set_state(NewTransaction.price)
    await message.answer("Введите цену траты в виде '120.00'.")


@transactions_router.message(NewTransaction.price)
async def process_transaction_price(message:Message, state: FSMContext):
    """
    Обрабатывает ввод цены траты. 
    Сохраняет транзакцию в БД.
    Завершает процесс добавления.
    """
    await state.update_data(price=message.text)
    data = await state.get_data()
    user_id = message.from_user.id
    try:
        transaction = await create_transaction(user_telegram_id=user_id,
                                            name=data["name"],
                                            price=decimal.Decimal(data["price"]))
        await message.answer(f"Трата '{transaction}' успешно добавлено в ваши траты.")
    except Exception:
        await message.answer("Вы ввели неправильные данные, попробуйте еще раз.")
    await state.clear()
