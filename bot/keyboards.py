from pymongo import MongoClient
from aiogram import types

from bot.config_reader import load_config


cluster = MongoClient(load_config("config/bot.ini").helper_bot.cluster_link)
collection = cluster['test']['users']


''' START '''


def start() -> types.InlineKeyboardMarkup:
    return make_menu(['Пароли'], ['passwords'])
    # return make_menu(['Заметки', 'Напоминания', 'Пароли'], ['notes', 'reminders', 'passwords'])


''' SETTINGS '''


def settings_start() -> types.InlineKeyboardMarkup:
    return make_menu(['Настройки генирации', 'Выход'], ['settings_generation', 'settings_exit'])


def settings_generation() -> types.InlineKeyboardMarkup:
    return make_menu(
        ['Длину пароля', 'Символы в пароле', 'Назад'],
        ['settings_generation_' + i for i in ['len', 'alphabet', 'back']]
    )


def settings_generation_len() -> types.InlineKeyboardMarkup:
    return make_menu(
        ['-1', '+1', '-2', '+2', '-5', '+5', 'Подтвердить'],
        ['settings_generation_len_' + i for i in ['-1', '1', '-2', '2', '-5', '5', 'apply']]
    )


''' PASSWORDS '''


def passwords_start(user_id: int) -> types.InlineKeyboardMarkup:
    callback_start = 'passwords_'
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    buttons = []

    for password_group_title in collection.find_one({'_id': user_id})['passwords'].keys():
        buttons.append(
            types.InlineKeyboardButton(
                text=password_group_title,
                callback_data=callback_start + password_group_title
            )
        )

    keyboard.add(*buttons)
    keyboard.add(*[
        types.InlineKeyboardButton(text='Добавить', callback_data=callback_start + 'add'),
        types.InlineKeyboardButton(text='Назад', callback_data=callback_start + 'back'),
    ])

    return keyboard


def get_passwords(user_id: int, callback: str) -> types.InlineKeyboardMarkup:
    callback_start = 'passwords_'
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    buttons = []

    for password_title in collection.find_one({'_id': user_id})['passwords'][callback.split('_')[1]].keys():
        buttons.append(
            types.InlineKeyboardButton(
                text=password_title,
                callback_data=callback_start + callback + password_title
            )
        )

    keyboard.add(*buttons)
    keyboard.add(*[
        types.InlineKeyboardButton(text='Добавить', callback_data=callback_start + callback + 'add'),
        types.InlineKeyboardButton(text='Назад', callback_data=callback_start + callback + 'back'),
    ])

    return keyboard


def show_password(callback: str) -> types.InlineKeyboardMarkup:
    return make_menu(
        ['Удалить', 'Переместить', 'Назад'],
        ['passwords_password_' + callback + i for i in ['delete', 'move', 'back']]
    )


def generation() -> types.InlineKeyboardMarkup:
    return make_menu(['Другой', 'Готово'], ['passwords_password_generation_' + i for i in ['another', 'apply']])


''' NOTES '''


def notes(user_id: int) -> types.InlineKeyboardMarkup:
    callback_start = 'notes_'
    keyboard = types.InlineKeyboardMarkup(row_width=3)

    buttons = [
        types.InlineKeyboardButton(text='Добавить', callback_data=callback_start + 'add_note'),
        types.InlineKeyboardButton(text='Удалить', callback_data=callback_start + 'delete_note')
    ]

    keyboard.add(*buttons)

    buttons = []

    passwords = collection.find_one({'_id': user_id})['notes']

    for password_title in passwords.keys():
        buttons.append(
            types.InlineKeyboardButton(
                text=password_title,
                callback_data=callback_start + 'show_' + password_title
            )
        )

    keyboard.add(*buttons)
    keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data=callback_start + 'back'))

    return keyboard


def get_notes(user_id: int, callback: str) -> types.InlineKeyboardMarkup:
    callback_start = 'notes_'
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    buttons = []

    _notes = collection.find_one({'_id': user_id})['notes']

    for note_title in _notes.keys():
        buttons.append(
            types.InlineKeyboardButton(
                text=note_title,
                callback_data=callback_start + callback + note_title
            )
        )

    keyboard.add(*buttons)
    keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data=callback_start + callback + 'back'))

    return keyboard


''' MAKE MENU FUNCTION '''


def make_menu(buttons_texts: list, callbacks: list, row_width: int = 2) -> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup(row_width=row_width)
    buttons = []

    for button_text, callback in zip(buttons_texts, callbacks):
        buttons.append(types.InlineKeyboardButton(text=button_text, callback_data=callback))

    return keyboard.add(*buttons)
