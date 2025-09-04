"""Вспомогательные функции."""
import datetime


def get_current_month() -> tuple[datetime.date, datetime.date]:
    """Возвращает начальную и конечную дату для текущего месяца."""
    current_month = datetime.date.today().month
    current_year = datetime.date.today().year
    start_date = datetime.date(current_year, current_month, 1)

    if current_month == 12:
        end_date = datetime.date(current_year + 1, 1, 1)
    else:
        end_date = datetime.date(current_year, current_month + 1, 1)

    return start_date, end_date