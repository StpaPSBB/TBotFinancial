"""Настройки для проекта."""
from dotenv import load_dotenv
import os


load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")


TORTOISE_ORM = {
    "connections": {"default": f"postgres://{os.getenv("POSTGRES_USER")}:{os.getenv("POSTGRES_PASSWORD")}@localhost:{os.getenv("POSTGRES_PORT")}/{os.getenv("POSTGRES_DB")}"},
    "apps": {
        "models": {
            "models": ["src.database.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}
