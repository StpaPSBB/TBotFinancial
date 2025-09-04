"""CRUD и работа с базой данных."""
import datetime
import decimal
import uuid
from typing import Any
from tortoise.functions import Sum
from tortoise.exceptions import DoesNotExist, ParamsError
from src.utils.logger import setup_module_logger
from src.utils.helpers import get_current_month
from .models import User, Transaction


logger = setup_module_logger(__name__)


async def get_or_create_user(telegram_id: int,
                             name: str) -> tuple[User|None, bool]:
    """Создает или получает пользователя."""
    try:
        user, created = await User.get_or_create(
            telegram_id=telegram_id,
            defaults={
                "name": name,
                "created_at": datetime.date.today(),
            }
        )
        if created:
            logger.info("Новый пользователь %s успешно добавлен в базу данных.", user.name)
        return user, created
    except Exception as e:
        logger.error("Ошибка при создании или получении пользователя: %s", e, exc_info=True)
        return None, False


async def create_transaction(user_telegram_id: int,
                             name: str,
                             price: decimal.Decimal,
                             created_at: datetime.date = datetime.date.today()) -> str|None:
    """Создание транзакции."""
    try:
        user = await User.get(telegram_id=user_telegram_id)
        if created_at < user.created_at:
            raise ValueError("Дата транзакции не может быть раньше даты создания пользователя")
        transaction = await Transaction.create(
            id=uuid.uuid4(),
            user_telegram_id=user,
            name=name,
            price=price,
            created_at=created_at,
        )
        logger.info("Новая транзакция пользователя %s - %s успешно добавлена.", 
                   user.name, transaction.name)
        return transaction.name
    except DoesNotExist:
        logger.error("Пользователь с telegram_id %s не найден.", user_telegram_id)
        return None
    except ParamsError as e:
        logger.error("Ошибка в переданных аргументах: %s", e, exc_info=True)
        return None
    except ValueError as e:
        logger.error("Ошибка валидации даты: %s", e, exc_info=True)
        return None
    except Exception as e:
        logger.error("Ошибка при добавлении транзакции: %s", e, exc_info=True)
        return None


async def edit_transaction(transaction_id: str,
                           name: str|None = None,
                           price: decimal.Decimal|None = None) -> bool:
    """Редактирует транзакцию."""
    try:
        transaction = await Transaction.get(id=transaction_id)
        transaction.name = name
        transaction.price = price
        await transaction.save()
        logger.info("Транзакция %s успешно отредактирована.", transaction_id)
        return True
    except DoesNotExist:
        logger.error("Транзакция с id %s не найдена.", transaction_id)
        return False
    except ParamsError as e:
        logger.error("Ошибка в переданных аргументах: %s", e, exc_info=True)
        return False
    except Exception as e:
        logger.error("Ошибка при редактировании транзакции: %s", e, exc_info=True)
        return False


async def delete_transaction(transaction_id: str) -> bool:
    """Удаляет транзакцию."""
    try:
        transaction = await Transaction.get(id=transaction_id)
        await transaction.delete()
        logger.info("Транзакция %s успешно удалена.", transaction_id)
        return True
    except DoesNotExist:
        logger.error("Транзакция с id %s не найдена.", transaction_id)
        return False
    except Exception as e:
        logger.error("Ошибка при удалении транзакции: %s", e, exc_info=True)
        return False


async def get_month_transactions(user_telegram_id: int) -> list[dict[str, Any]]|None:
    """Возвращает список транзакций за текущий месяц для данного пользователя."""
    try:
        user =  await User.get(telegram_id=user_telegram_id)
        start_date, end_date = get_current_month()
        transactions = await Transaction.filter(
            user_telegram_id=user,
            created_at__gte=start_date,
            created_at__lt=end_date).values("id", "name", "price", "created_at")
        logger.info("Транзакции для пользователя %s за месяц %s успешно получены.",
                    user.name, start_date.month)
        return transactions
    except DoesNotExist:
        logger.error("Пользователь с telegram_id %s не найден.", user_telegram_id)
        return None
    except Exception as e:
        logger.error("Ошибка при получении транзакций за текущий месяц: %s", e, exc_info=True)
        return None



async def get_month_transactions_price(user_telegram_id: int) -> decimal.Decimal|None:
    """Возвращает общие траты за месяц."""
    try:
        user =  await User.get(telegram_id=user_telegram_id)
        start_date, end_date = get_current_month()
        result = await Transaction.filter(
            user_telegram_id=user,
            created_at__gte=start_date,
            created_at__lt=end_date
        ).annotate(total = Sum("price")).values("total")
        total_price = result[0]['total'] if result else decimal.Decimal('0')
        logger.info("Успешно посчитаны общие расходы пользователя %s за месяц %s.",
                    user.name, start_date.month)
        return total_price
    except DoesNotExist:
        logger.error("Пользователь с telegram_id %s не найден.", user_telegram_id)
        return None
    except Exception as e:
        logger.error("Ошибка при вычислении общих расходов за месяц: %s", e, exc_info=True)
        return None


async def get_today_transactions(user_telegram_id: int) -> list[dict[str, Any]]|None:
    """Возвращает список трат за текущий день для данного пользователя."""
    try:
        today = datetime.date.today()
        user = await User.get(telegram_id=user_telegram_id)
        transactions = await Transaction.filter(
            user_telegram_id=user,
            created_at=today
        ).values("id", "name", "price", "created_at")
        logger.info("Транзакции для пользователя %s за текущий день %s успешно получены.",
                    user.name, today)
        return transactions
    except DoesNotExist:
        logger.error("Пользователь с telegram_id %s не найден.", user_telegram_id)
        return None


async def get_today_transactions_price(user_telegram_id: int) -> decimal.Decimal|None:
    """Возвращает общие траты за день."""
    try:
        today = datetime.date.today()
        user =  await User.get(telegram_id=user_telegram_id)
        start_date, end_date = get_current_month()
        result = await Transaction.filter(
            user_telegram_id=user,
            created_at=today
        ).annotate(total = Sum("price")).values("total")
        total_price = result[0]['total'] if result else decimal.Decimal('0')
        logger.info("Успешно посчитаны общие расходы пользователя %s за день %s.",
                    user.name, today)
        return total_price
    except DoesNotExist:
        logger.error("Пользователь с telegram_id %s не найден.", user_telegram_id)
        return None
    except Exception as e:
        logger.error("Ошибка при вычислении общих расходов за день: %s", e, exc_info=True)
        return None
