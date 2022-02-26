from pymongo import MongoClient

from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text

from bot.config_reader import load_config
import bot.keyboards as k


cluster = MongoClient(load_config("config/bot.ini").helper_bot.cluster_link)
collection = cluster['test']['users']


def get_generation_settings(user_id: int):
    generation_settings = collection.find_one({'_id': user_id})['generation-settings']

    alphabet = 'Латиница в обоих регистрах'

    for generation_setting in generation_settings['alphabet'].split():
        if generation_setting == 'nums':
            alphabet += ' + цифры'
        else:
            alphabet += f' + {generation_setting}'

    return f'Длина пароля: <b>{generation_settings["len"]}</b>\n'\
           f'Символы в пароле: <b>{alphabet}</b>\n\n'


def get_settings(user_id: int) -> str:
    return 'Вот твои текущие настрокий:\n\n' \
           'Генерация пароля:\n' + get_generation_settings(user_id)


async def settings_start(message: types.Message):
    await message.delete()
    await message.answer(
        get_settings(message.from_user.id) + 'Что будем менять?',
        reply_markup=k.settings_start()
    )


async def settings(call: types.CallbackQuery):
    data = call.data.split('_')

    match len(data):
        case 2:
            match data[1]:
                case 'exit':
                    await call.message.edit_text('Удачи!')
                    return
                case 'generation':
                    await call.message.edit_text(
                        get_generation_settings(call.message.chat.id) + 'Что будем менять?',
                        reply_markup=k.settings_generation()
                    )


async def settings_generation(call: types.CallbackQuery):
    data = call.data.split('_')[2]
    match data:
        case 'back':
            await call.message.edit_text(
                get_settings(call.message.chat.id) + 'Что будем менять?',
                reply_markup=k.settings_start()
            )
        case 'len':
            await call.message.edit_text(
                get_generation_settings(call.message.chat.id),
                reply_markup=k.settings_generation_len()
            )
        case 'alphabet':
            await call.message.edit_text(
                get_settings(call.message.chat.id) + 'Что будем менять?',
                reply_markup=k.settings_start()
            )


async def settings_generation_len(call: types.CallbackQuery):
    data = call.data.split('_')[3]
    match data:
        case 'apply':
            await call.message.edit_text(
                get_generation_settings(call.message.chat.id) + 'Что будем менять?',
                reply_markup=k.settings_generation()
            )
        case _:
            generation_settings = collection.find_one({'_id': call.message.chat.id})['generation-settings']

            len_ = generation_settings['len']
            len_ += int(data)

            if 20 >= len_ >= 6:
                generation_settings['len'] = len_

                collection.update_one(
                    {'_id': call.message.chat.id},
                    {'$set': {'generation-settings': generation_settings}}
                )
                await call.message.edit_text(
                    get_generation_settings(call.message.chat.id),
                    reply_markup=k.settings_generation_len()
                )
            await call.answer()


async def settings_generation_alphabet(call: types.CallbackQuery):
    data = call.data.split('_')[3]
    print(data)


def rh_settings(dp: Dispatcher):
    dp.register_message_handler(settings_start, commands="settings")
    dp.register_callback_query_handler(settings_generation_alphabet, Text(startswith='settings_generation_alphabet_'))
    dp.register_callback_query_handler(settings_generation_len, Text(startswith='settings_generation_len_'))
    dp.register_callback_query_handler(settings_generation, Text(startswith='settings_generation_'))
    dp.register_callback_query_handler(settings, Text(startswith='settings'))
