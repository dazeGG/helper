from bot.crypt import _generate_keys, _load_keys, _encrypt, _decrypt
# import asyncio

from bot.config import collection


async def crypto_keys_changer():
    # while True:
    old_public_key, old_private_key = _load_keys()
    _generate_keys()
    new_public_key, new_private_key = _load_keys()

    for user in collection.find():
        try:
            for passwords_group in user['passwords'].items():
                for password in passwords_group[1].items():
                    decrypted_password = _decrypt(password[1], old_private_key)
                    password_encrypted_by_new_keys = _encrypt(decrypted_password, new_public_key)
                    user['passwords'][passwords_group[0]][password[0]] = password_encrypted_by_new_keys
            collection.update_one({'_id': user['_id']}, {'$set': {'passwords': user['passwords']}})
        except KeyError:
            pass

    print('changing crypto keys success!!')

    # await asyncio.sleep(3600)
