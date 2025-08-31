"""Состояния FSM для бота."""
from aiogram.fsm.state import StatesGroup, State

class NewTransaction(StatesGroup):
    """Состояние FSM для добавления новой траты."""
    name = State()
    price = State()
