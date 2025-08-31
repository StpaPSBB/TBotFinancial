"""CRUD и работа с базой данных."""
import datetime
import decimal
import uuid
from tortoise.functions import Sum
from tortoise.exceptions import DoesNotExist, ParamsError
from src.utils.logger import setup_module_logger
from .models import User, Transaction


logger = setup_module_logger(__name__)


def _get_current_month() -> tuple[datetime.date, datetime.date]:
    """Возвращает начальную и конечную дату для текущего месяца."""
    current_month = datetime.date.today().month
    current_year = datetime.date.today().year
    start_date = datetime.date(current_year, current_month, 1)

    if current_month == 12:
        end_date = datetime.date(current_year + 1, 1, 1)
    else:
        end_date = datetime.date(current_year, current_month + 1, 1)

    return start_date, end_date


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
                             price: decimal.Decimal):
    """Создание транзакции."""
    try:
        user = await User.get(telegram_id=user_telegram_id)
        transaction = await Transaction.create(
            id=uuid.uuid4(),
            user_telegram_id=user,
            name=name,
            price=price,
            created_at=datetime.date.today(),
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
    except Exception as e:
        logger.error("Ошибка при добавлении транзакции: %s", e, exc_info=True)
        return None


async def get_month_transactions(user_telegram_id: int):
    """Получает все транзакции за текущий месяц для данного пользователя."""
    try:
        user =  await User.get(telegram_id=user_telegram_id)
        start_date, end_date = _get_current_month()
        transactions = await Transaction.filter(user_telegram_id=user,
                                                created_at__gte=start_date,
                                                created_at__lt=end_date)
        logger.info("Транзакции для пользователя %s за месяц %s успешно получены.", user.name, start_date.month)
        transactions_list = []
        for transaction in transactions:
            transactions_list.append({
                "name": transaction.name,
                "price": transaction.price,
                "created_at": transaction.created_at 
            })
        return transactions_list
    except DoesNotExist:
        logger.error("Пользователь с telegram_id %s не найден.", user_telegram_id)
        return None
    except Exception as e:
        logger.error("Ошибка при получении транзакций за текущий месяц: %s", e, exc_info=True)
        return None



async def get_month_transactions_price(user_telegram_id: int):
    """Возвращает общие траты за месяц."""
    try:
        user =  await User.get(telegram_id=user_telegram_id)
        start_date, end_date = _get_current_month()
        result = await Transaction.filter(
            user_telegram_id=user,
            created_at__gte=start_date,
            created_at__lt=end_date
        ).annotate(total = Sum("price")).values("total")
        total_price = result[0]['total'] if result else decimal.Decimal('0')
        logger.info("Успешно посчитаны общие расходы пользователя %s за месяц %s.", user.name, start_date.month)
        return total_price
    except Exception as e:
        logger.error("Ошибка при вычислении общих расходов за месяц: %s", e, exc_info=True)
        return None