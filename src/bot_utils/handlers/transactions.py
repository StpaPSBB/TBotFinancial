"""Хендлеры для работы с транзакциями."""
import decimal
import datetime
from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from src.database.services import (create_transaction, get_month_transactions, get_month_transactions_price,
                                   get_today_transactions, get_today_transactions_price, edit_transaction, delete_transaction)
from src.bot_utils.keyboards.main_inline_kb import edit_delete_inline_kb, date_inline_kb
from .states import NewTransaction, EditTransaction

transactions_router = Router()


@transactions_router.message(F.text == "Показать траты за месяц")
async def show_month_transactions(message: Message):
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
            kb = edit_delete_inline_kb(transaction_id=transaction["id"])
            await message.answer(f"{idx}. Трата: {name}. Цена: {price} рублей. Дата: {date}", reply_markup=kb)
        await message.answer(f"Общие траты за месяц - {total_price:.2f} рублей.")
    else:
        await message.answer("Вы пока не добавляли никаких трат в этом месяце.")


@transactions_router.message(F.text == "Показать траты за сегодня")
async def show_today_transactions(message: Message):
    """
    Обрабатывает команду 'Показать траты за сегодня'.
    Выводит траты за сегодняшний день и общую их стоимость.
    """
    user_id = message.from_user.id
    transactions = await get_today_transactions(user_telegram_id=user_id)
    total_price = await get_today_transactions_price(user_telegram_id=user_id)
    if transactions:    
        for i, transaction in enumerate(transactions, 1):
            idx = i
            name = transaction["name"]
            price = transaction["price"]
            date = transaction["created_at"]
            kb = edit_delete_inline_kb(transaction_id=transaction["id"])
            await message.answer(f"{idx}. Трата: {name}. Цена: {price} рублей. Дата: {date}", reply_markup=kb)
        await message.answer(f"Общие траты за сегодня - {total_price:.2f} рублей.")
    else:
        await message.answer("Вы пока не добавляли никаких трат сегодня.")


@transactions_router.message(F.text == "Добавить трату")
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
async def process_transaction_price(message: Message, state: FSMContext):
    """Обрабатывает ввод цены и запрашивает дату."""
    await state.update_data(price=message.text)
    await state.set_state(NewTransaction.date)
    kb = date_inline_kb()
    await message.answer("Введите дату для этой траты.", reply_markup=kb)


@transactions_router.callback_query(F.data == "today")
async def process_transaction_today(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает кнопку сегодняшней даты."""
    await state.update_data(date=datetime.date.today())
    data = await state.get_data()
    user_id = callback.from_user.id
    transaction = await create_transaction(user_telegram_id=user_id,
                                        name=data["name"],
                                        price=decimal.Decimal(data["price"]))
    if transaction:    
        await callback.message.answer(f"Трата '{transaction}' успешно добавлена в ваши траты.")
    else:
        await callback.message.answer("Вы ввели неправильные данные, попробуйте еще раз.")
    await callback.answer()
    await state.clear()


@transactions_router.callback_query(F.data == "another_date")
async def process_transaction_another_date(callback: CallbackQuery):
    """Обрабатывает кнопку для другой даты."""
    await callback.message.answer("Ведите дату в виде '11.11.1111'")
    await callback.answer()


@transactions_router.message(NewTransaction.date)
async def process_transaction_date(message:Message, state: FSMContext):
    """
    Обрабатывает ввод даты траты. 
    Сохраняет транзакцию в БД.
    Завершает процесс добавления.
    """
    await state.update_data(date=message.text)
    data = await state.get_data()
    day, month, year = map(int, data["date"].split('.'))
    user_id = message.from_user.id
    transaction = await create_transaction(user_telegram_id=user_id,
                                            name=data["name"],
                                            price=decimal.Decimal(data["price"]),
                                            created_at=datetime.date(year, month, day))
    if transaction:    
        await message.answer(f"Трата '{transaction}' успешно добавлена в ваши траты.")
    else:
        await message.answer("Вы ввели неправильные данные, попробуйте еще раз.")
    await state.clear()


@transactions_router.callback_query(F.data.startswith("edit"))
async def start_edditing_transaction(callback: CallbackQuery, state: FSMContext):
    """
    Начинает процесс изменения траты.
    Задает имя транзакции.
    """
    await state.set_state(EditTransaction.id)
    await state.update_data(id=callback.data.split("_")[1])
    await state.set_state(EditTransaction.name)
    await callback.message.answer("Введите новое название траты.")
    await callback.answer()


@transactions_router.message(EditTransaction.name)
async def process_new_transaction_name(message: Message, state: FSMContext):
    """Обрабатывает ввод нового названия траты и запрашивает цену."""
    await state.update_data(name=message.text)
    await state.set_state(EditTransaction.price)
    await message.answer("Введите новую цену траты в виде '120.00'.")


@transactions_router.message(EditTransaction.price)
async def process_new_transaction_price(message:Message, state: FSMContext):
    """
    Обрабатывает ввод новой цены траты. 
    Изменяет транзакцию в БД.
    Завершает процесс изменения.
    """
    await state.update_data(price=message.text)
    data = await state.get_data()
    transaction = await edit_transaction(transaction_id=data["id"],
                                            name=data["name"],
                                            price=decimal.Decimal(data["price"]))
    if transaction:    
        await message.answer(f"Трата '{data["name"]}' успешно добавлена в ваши траты.")
    else:
        await message.answer("Вы ввели неправильные данные, попробуйте еще раз.")
    await state.clear()


@transactions_router.callback_query(F.data.startswith("delete"))
async def delete_chosen_transaction(callback: CallbackQuery):
    """Удаляет выбранную трату."""
    await delete_transaction(transaction_id=callback.data.split("_")[1])
    await callback.message.answer("Выбранная трата успешно удалена.")
    await callback.answer()