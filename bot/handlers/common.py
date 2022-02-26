from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError

from aiogram import Dispatcher, types

from bot.config_reader import load_config
import bot.keyboards as k


cluster = MongoClient(load_config("config/bot.ini").helper_bot.cluster_link)
collection = cluster['test']['users']


async def start(message: types.Message):
    try:
        collection.insert_one({
            '_id': message.from_user.id,
            'passwords': {'other': {}},
            'generation-settings': {'len': 15, 'alphabet': "def"},
            'tmp': {'tmp-password-title': '', 'chosen-group': ''},
        })
    except DuplicateKeyError:
        pass
    await message.answer('Привет, я твой персональный помощник! Выбери категорию.', reply_markup=k.start())


def rh_common(dp: Dispatcher):
    dp.register_message_handler(start, commands="start")
