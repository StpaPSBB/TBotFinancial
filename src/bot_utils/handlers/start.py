"""Сартовый хендлер."""
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from src.database.services import get_or_create_user
import src.bot_utils.keyboards.main_reply_kb as kb


start_router = Router()


@start_router.message(CommandStart())
async def cmd_start(message: Message):
    """Обрабатывает команду /start"""
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    user, created = await get_or_create_user(telegram_id=user_id, name=user_name)
    if created:    
        await message.answer(f"Привет, {user_name}! Я бот для учета финансов." \
                              "Для помощи в моей работе используй команду: /help.",
                             reply_markup=kb.main)
    else:
        await message.answer(f"Привет, {user_name}! Мы уже знакомы!",
                             reply_markup=kb.main)


@start_router.message(Command("help"))
async def cmd_help(message: Message):
    """Обрабатывает команду /help"""
    await message.answer("Я бот для учета личных расходов. \n" \
                         "Ты можешь добавлять новые траты за день" \
                         "и получить список трат за текущий месяц.")