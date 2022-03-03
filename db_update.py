from bot.config import collection


if __name__ == '__main__':

    '''
    public_key, private_key = _load_keys()

    for user in collection.find():
        print(user)
        for group_key in user['passwords'].keys():
            for password_key in user['passwords'][group_key].keys():
                encrypted_password = _encrypt(user['passwords'][group_key][password_key], public_key)
                user['passwords'][group_key][password_key] = encrypted_password
        collection.update_one({'_id': user['_id']}, {'$set': {'passwords': user['passwords']}})
    '''

    # collection.update_one({'_id': user['_id']}, {'$set': {'generation-settings': user['generation-settings']}})
    # collection.update_one({'_id': user['_id']}, {'$set': {'tmp': user['tmp']}})
    # collection.update_one({'_id': user['_id']}, {'$unset': {'generation_settings': ''}})
    # collection.update_one({'_id': i['_id']}, {'$set': {'tmp_password_title': ''}})
    # collection.update_one({'_id': i['_id']}, {'$set': {'generation_settings': {'len': 12, 'alphabet': 'def'}}})
