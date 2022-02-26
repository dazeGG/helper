from pymongo import MongoClient
# from pymongo.errors import DuplicateKeyError

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import MessageNotModified

from bot.config_reader import load_config
import bot.keyboards as k

cluster = MongoClient(load_config("config/bot.ini").helper_bot.cluster_link)
collection = cluster['test']['users']

choose = 'заметку'


class Notes(StatesGroup):
    add_note_title = State()
    add_note_data = State()


async def lol(call: types.CallbackQuery):
    data = call.data.split('_')
    print('lol', data)
    match len(data):
        case 1:
            await call.message.edit_text(
                text=f'Выбери {choose} или действие.',
                reply_markup=k.notes(call.message.chat.id)
            )
        case 2 | 3:
            match data[1]:
                case 'back':
                    await call.message.edit_text(text='Выбери категорию.', reply_markup=k.start())
                case 'add':
                    match len(data):
                        case 3:
                            match data[2]:
                                case 'note':
                                    await call.message.delete()
                                    await call.message.answer(
                                        'Введи название заметки.',
                                        reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add(*['отмена'])
                                    )
                                    await Notes.add_note_title.set()
                                    await call.answer()
                case 'show':
                    if data[2] == 'back':
                        await call.message.edit_text(
                            text=f'Выбери {choose} или действие.',
                            reply_markup=k.notes(call.message.chat.id)
                        )
                        await call.answer()
                    else:
                        note = collection.find_one({'_id': call.message.chat.id})['notes'][data[2]]
                        try:
                            await call.message.edit_text(
                                text=f'<b>{note}</b>',
                                reply_markup=k.get_notes(user_id=call.message.chat.id, callback='show_')
                            )
                        except MessageNotModified:
                            pass
                        await call.answer()
    await call.answer()


async def delete(call: types.CallbackQuery):
    data = call.data.split('_')
    print('delete', data)
    match len(data):
        case 3:
            match data[2]:
                case 'note':
                    await call.message.edit_text(
                        text='Какой?',
                        reply_markup=k.get_notes(
                            user_id=call.message.chat.id,
                            callback='delete_note_'
                        )
                    )
                    await call.answer()
        case 4:
            match data[2]:
                case 'note':
                    if data[3] != 'back':
                        notes = collection.find_one({'_id': call.message.chat.id})['notes']
                        notes.pop(data[3])

                        collection.update_one(
                            {'_id': call.message.chat.id},
                            {'$set': {'notes': notes}}
                        )

                        await call.message.edit_text(
                            text=f'Выбери {choose} или действие.',
                            reply_markup=k.notes(call.message.chat.id)
                        )
                        await call.answer()
                    else:
                        await call.message.edit_text(
                            text=f'Выбери {choose} или действие.',
                            reply_markup=k.notes(call.message.chat.id)
                        )
                        await call.answer()
    await call.answer()


async def add_note_title(message: types.Message, state: FSMContext):
    if message.text.lower() == 'отмена':
        await message.answer('Не добавил заметку.')
        await message.answer(
            f'Выбери {choose} или действие.',
            reply_markup=k.notes(message.from_user.id)
        )
        await state.finish()
        await Notes.add_note_data.set()


async def add_note_data(message: types.Message, state: FSMContext):
    tmp_title = collection.find_one({'_id': message.from_user.id})['tmp_note_title']

    notes = collection.find_one({'_id': message.from_user.id})['notes']
    notes[tmp_title] = message.text

    collection.update_one({'_id': message.from_user.id}, {'$set': {'notes': notes}})
    await message.answer('Успешно добавили заметку.')
    await message.answer(
        text=f'Выбери {choose} или действие.',
        reply_markup=k.notes(message.from_user.id))
    await state.finish()


def rh_passwords(dp: Dispatcher):
    dp.register_callback_query_handler(delete, Text(startswith='notes_delete'))
    dp.register_callback_query_handler(lol, Text(startswith='notes'))
    dp.register_message_handler(add_note_title, state=Notes.add_note_title)
    dp.register_message_handler(add_note_data, state=Notes.add_note_data)
