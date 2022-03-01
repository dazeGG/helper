import logging
from asyncio import run

from pymongo import MongoClient

from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from bot.config_reader import load_config

from bot.crypto_keys_changer import crypto_keys_changer

from bot.handlers.common import rh_common
# from bot.handlers.settings import rh_settings
from bot.handlers.password import rh_passwords


config = load_config("config/bot.ini")

bot = Bot(token=config.helper_bot.token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot=bot, storage=MemoryStorage())


cluster = MongoClient(config.helper_bot.cluster_link)
collection = cluster['test']['users']


async def set_commands():
    await dp.bot.set_my_commands([
        types.BotCommand(command="/start", description="Начало"),
        types.BotCommand(command="/settings", description="Настройки"),
    ])


def log():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
    logger = logging.getLogger(__name__)
    logger.error("Starting bot")


async def main():
    log()

    await crypto_keys_changer()

    rh_common(dp)
    # rh_settings(dp)
    rh_passwords(dp)

    await set_commands()
    await dp.start_polling()


if __name__ == '__main__':
    run(main())
