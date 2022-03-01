from bot.crypt import _generate_keys, _load_keys, _encrypt, _decrypt
from pymongo import MongoClient
import asyncio

from bot.config_reader import load_config


config = load_config("config/bot.ini")

cluster = MongoClient(config.helper_bot.cluster_link)
collection = cluster['test']['users']


async def crypto_keys_changer():
    # while True:
    old_public_key, old_private_key = _load_keys()
    _generate_keys()
    new_public_key, new_private_key = _load_keys()

    for user in collection.find():
        for passwords_group in user['passwords'].items():
            for password in passwords_group[1].items():
                decrypted_password = _decrypt(password[1], old_private_key)
                password_encrypted_by_new_keys = _encrypt(decrypted_password, new_public_key)
                user['passwords'][passwords_group[0]][password[0]] = password_encrypted_by_new_keys
        collection.update_one({'_id': user['_id']}, {'$set': {'passwords': user['passwords']}})

    print('changing crypto keys success!!')

    # await asyncio.sleep(3600)
