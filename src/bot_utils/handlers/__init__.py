"""Хендлеры для бота."""
from .start import start_router
from .transactions import transactions_router


routers = [start_router, transactions_router]