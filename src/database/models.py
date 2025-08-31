"""Модели для Telegram бота."""
from tortoise.models import Model
from tortoise import fields


class User(Model):
    """Модель для пользователя."""
    telegram_id = fields.IntField(primary_key=True)
    name = fields.CharField(max_length=150)
    created_at = fields.DateField()


    class Meta:
        table = "Users"


class Transaction(Model):
    """Модель для транзакции."""
    id = fields.UUIDField(primary_key=True)
    user_telegram_id = fields.ForeignKeyField(model_name="models.User")
    name = fields.TextField(max_length=300)
    price = fields.DecimalField(max_digits=10, decimal_places=2)
    created_at = fields.DateField()


    class Meta:
        table = "Transactions"
