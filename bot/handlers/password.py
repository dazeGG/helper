from pymongo import MongoClient

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import MessageNotModified

from bot.crypt import _load_keys, _encrypt, _decrypt
from bot.config_reader import load_config
import bot.keyboards as k
import bot.scripts as sc


cluster = MongoClient(load_config("config/bot.ini").helper_bot.cluster_link)
collection = cluster['test']['users']

choose_group = 'Выбери группу паролей.'
choose_password = 'Выбери пароль.'

alf = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'


class Password(StatesGroup):
    add_password_title = State()
    add_password_data = State()


class Group(StatesGroup):
    set_group_title = State()


async def _passwords(call: types.CallbackQuery):
    data = call.data.split('_')
    print(data)
    match len(data):
        case 1:
            await call.message.edit_text(
                text=choose_group,
                reply_markup=k.passwords_start(call.message.chat.id)
            )
        case 2:
            match data[1]:
                case 'back':
                    await call.message.edit_text(
                        text='Выбери категорию.',
                        reply_markup=k.start()
                    )
                case 'add':
                    await call.message.delete()
                    await call.message.answer(
                        text='Напиши название группы.',
                        reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(*['отмена'])
                    )
                    await Group.set_group_title.set()
                case _:
                    await call.message.edit_text(
                        text=choose_password,
                        reply_markup=k.get_passwords(call.message.chat.id, f'group_{data[1]}_')
                    )
                    collection.update_one({'_id': call.message.chat.id},
                                          {'$set': {'tmp': {'tmp-password-title': '', 'chosen-group': data[1]}}})
    await call.answer()


async def show_group(call: types.CallbackQuery):
    public_key, private_key = _load_keys()
    data = call.data.split('_')
    print(data)
    match data[3]:
        case 'back':
            await call.message.edit_text(
                text=choose_group,
                reply_markup=k.passwords_start(call.message.chat.id)
            )
            collection.update_one({'_id': call.message.chat.id},
                                  {'$set': {'tmp': {'tmp-password-title': '', 'chosen-group': ''}}})
        case 'add':
            await call.message.delete()
            await call.message.answer(
                'Напиши ключ для пароля.',
                reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(*['отмена'])
            )
            await Password.add_password_title.set()
            collection.update_one({'_id': call.message.chat.id},
                                  {'$set': {'tmp': {'tmp-password-title': '', 'chosen-group': data[2]}}})
        case _:
            encrypted_password = collection.find_one({'_id': call.message.chat.id})['passwords'][data[2]][data[3]]
            await call.message.edit_text(
                text=f"<b>{_decrypt(encrypted_password, private_key)}</b>",
                reply_markup=k.show_password(f'{data[2]}_{data[3]}_')
            )
    await call.answer()


async def show_password(call: types.CallbackQuery):
    public_key, private_key = _load_keys()
    data = call.data.split('_')
    print(data)
    if data[2] == 'generation':
        match data[3]:
            case 'another':
                password_len = collection.find_one({'_id': call.message.chat.id})['generation-settings']['len']
                await call.message.edit_text(
                    text=f'<b>{sc.generate_password(password_len, alf)}</b>',
                    reply_markup=k.generation()
                )
            case 'apply':
                await call.message.delete()

                tmp = collection.find_one({'_id': call.message.chat.id})['tmp']
                tmp_password_title = tmp['tmp-password-title']
                chosen_group = tmp['chosen-group']
                passwords = collection.find_one({'_id': call.message.chat.id})['passwords']

                passwords[chosen_group][tmp_password_title] = _encrypt(call.message.text, public_key)

                collection.update_one(
                    {'_id': call.message.chat.id},
                    {'$set': {'passwords': passwords, 'tmp': {'tmp-password-title': '', 'chosen-group': chosen_group}}}
                )
                await call.message.answer('Успешно добавил пароль.', reply_markup=types.ReplyKeyboardRemove())
                await call.message.answer(
                    text=choose_password,
                    reply_markup=k.get_passwords(call.message.chat.id, f'group_{chosen_group}_')
                )
        await call.answer()
        return
    match data[4]:
        case 'back':
            await call.message.edit_text(
                text=choose_password,
                reply_markup=k.get_passwords(call.message.chat.id, f'group_{data[2]}_')
            )
        case 'move':
            try:
                await call.message.edit_text(
                    text='Пока что я этого не умею, но скоро научусь и ты сможешь переместить пароль в другую группу)',
                    reply_markup=k.show_password(f'{data[2]}_{data[3]}_')
                )
            except MessageNotModified:
                pass
        case 'delete':
            passwords = collection.find_one({'_id': call.message.chat.id})['passwords']
            passwords[data[2]].pop(data[3])

            collection.update_one({'_id': call.message.chat.id}, {'$set': {'passwords': passwords}})
            await call.message.edit_text(
                text=choose_password,
                reply_markup=k.get_passwords(call.message.chat.id, f'group_{data[2]}_')
            )
    await call.answer()


async def set_group_title(message: types.Message, state: FSMContext):
    if message.text.lower() == 'отмена':
        await message.delete()
        await message.answer('Не добавил группу.', reply_markup=types.ReplyKeyboardRemove())
        await message.answer(
            text=choose_group,
            reply_markup=k.passwords_start(message.from_user.id)
        )
    elif message.text.lower() in ['password', 'group']:
        await message.answer('Недопустимое название группы. Попробуй другое.')
    else:
        passwords_groups = collection.find_one({'_id': message.from_user.id})['passwords']
        for passwords_group_title in passwords_groups.keys():
            if message.text.lower() == passwords_group_title.lower():
                await message.answer(
                    'Группа с таким названием уже есть, напиши <b>другое название</b> '
                    'или нажми кнопку <b>"отмена"</b>, если не хочешь добавлять группу)'
                )
                return
        passwords_groups[message.text] = {}
        collection.update_one({'_id': message.from_user.id}, {'$set': {'passwords': passwords_groups}})
        await message.answer(
            text=choose_group,
            reply_markup=k.passwords_start(message.from_user.id)
        )
    await state.finish()


async def add_password_title(message: types.Message, state: FSMContext):
    chosen_group = collection.find_one({'_id': message.from_user.id})['tmp']['chosen-group']
    if message.text.lower() == 'отмена':
        await message.delete()
        await message.answer('Не добавил пароль.', reply_markup=types.ReplyKeyboardRemove())
        await message.answer(
            text=choose_password,
            reply_markup=k.get_passwords(message.from_user.id, f'group_{chosen_group}_')
        )
        await state.finish()
        collection.update_one({'_id': message.from_user.id},
                              {'$set': {'tmp': {'tmp-password-title': '', 'chosen-group': chosen_group}}})
    elif message.text.lower() in ['password', 'group']:
        await message.answer('Недопустимый ключ пароля. Попробуй другое.')
    else:
        for password_title in collection.find_one({'_id': message.from_user.id})['passwords'][chosen_group].keys():
            if message.text.lower() == password_title.lower():
                await message.answer(
                    'Пароль с таким ключом уже есть, напиши <b>другой ключ</b> '
                    'или нажми кнопку <b>"отмена"</b>, если не хочешь добавлять пароль)'
                )
                return
        collection.update_one({'_id': message.from_user.id},
                              {'$set': {'tmp': {'tmp-password-title': message.text, 'chosen-group': chosen_group}}})
        await message.answer(
            text='Теперь напиши мне пароль или нажми кнопку <b>"сгенерировать"</b>, если хочешь сгенерировать пароль.',
            reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(*['сгенерировать'])
        )
        await Password.add_password_data.set()


async def add_password_data(message: types.Message, state: FSMContext):
    public_key, private_key = _load_keys()
    if message.text.lower() == 'сгенерировать':
        password_len = collection.find_one({'_id': message.from_user.id})['generation-settings']['len']
        await message.answer(text=f'<b>{sc.generate_password(password_len, alf)}</b>', reply_markup=k.generation())
    else:
        tmp = collection.find_one({'_id': message.from_user.id})['tmp']
        tmp_password_title = tmp['tmp-password-title']
        chosen_group = tmp['chosen-group']
        passwords = collection.find_one({'_id': message.from_user.id})['passwords']

        passwords[chosen_group][tmp_password_title] = _encrypt(message.text, public_key)

        collection.update_one(
            {'_id': message.from_user.id},
            {'$set': {'passwords': passwords, 'tmp': {'tmp-password-title': '', 'chosen-group': chosen_group}}}
        )
        await message.answer('Успешно добавил пароль.', reply_markup=types.ReplyKeyboardRemove())
        await message.answer(
            text=choose_password,
            reply_markup=k.get_passwords(message.from_user.id, f'group_{chosen_group}_')
        )
    await state.finish()


def rh_passwords(dp: Dispatcher):
    dp.register_callback_query_handler(show_password, Text(startswith='passwords_password'))
    dp.register_callback_query_handler(show_group, Text(startswith='passwords_group'))
    dp.register_callback_query_handler(_passwords, Text(startswith='passwords'))
    dp.register_message_handler(set_group_title, state=Group.set_group_title)
    dp.register_message_handler(add_password_title, state=Password.add_password_title)
    dp.register_message_handler(add_password_data, state=Password.add_password_data)
