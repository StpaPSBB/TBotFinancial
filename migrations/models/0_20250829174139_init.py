from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "Users" (
    "telegram_id" SERIAL NOT NULL PRIMARY KEY,
    "name" VARCHAR(150) NOT NULL,
    "created_at" DATE NOT NULL
);
COMMENT ON TABLE "Users" IS 'Модель для пользователя.';
CREATE TABLE IF NOT EXISTS "Transactions" (
    "id" UUID NOT NULL PRIMARY KEY,
    "name" TEXT NOT NULL,
    "price" DECIMAL(10,2) NOT NULL,
    "created_at" DATE NOT NULL,
    "user_telegram_id_id" INT NOT NULL REFERENCES "Users" ("telegram_id") ON DELETE CASCADE
);
COMMENT ON TABLE "Transactions" IS 'Модель для транзакции.';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
