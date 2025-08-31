"""Управление подключением к базе данных"""
from tortoise import Tortoise
from src.utils.logger import setup_module_logger


logger = setup_module_logger(__name__)


async def init_db_connection(db_config: dict) -> None:
    """Функция подключения к базе данных."""
    try:
        await Tortoise.init(config = db_config)
        await Tortoise.generate_schemas()
        logger.info("Подключение к базе данных успешно установленно.")
    except Exception as e:
        logger.error("Ошибка при подключении к базе данных: %s", e, exc_info=True)


async def close_db_connection() -> None:
    """Функци отключения от базы данных."""
    try:    
        await Tortoise.close_connections()
        logger.info("Подключение к базе данных успешно закрыто.")
    except Exception as e:
        logger.error("Ошибка при отключении от базе данных: %s", e, exc_info=True)