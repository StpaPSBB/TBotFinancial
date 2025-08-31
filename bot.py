"""Основной код бота."""
import asyncio
import settings
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from src.database.db_con import init_db_connection, close_db_connection
from src.database.services import get_or_create_user, create_transaction, get_month_transactions, get_month_transactions_price
from src.bot_utils.handlers import routers



bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()


async def main():
    await init_db_connection(db_config=settings.TORTOISE_ORM)
    dp.include_routers(*routers)
    await dp.start_polling(bot)
    await close_db_connection()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен.")
