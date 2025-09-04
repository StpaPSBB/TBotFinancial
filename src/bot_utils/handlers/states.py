"""Состояния FSM для бота."""
from aiogram.fsm.state import StatesGroup, State

class NewTransaction(StatesGroup):
    """Состояние FSM для добавления новой траты."""
    name = State()
    price = State()
    date = State()


class EditTransaction(StatesGroup):
    """Состояние FSM для изменения траты."""
    id = State()
    name = State()
    price = State()