from pymongo import MongoClient
from bot.config_reader import load_config


cluster = MongoClient(load_config("config/bot.ini").helper_bot.cluster_link)
collection = cluster['test']['users']


if __name__ == '__main__':
    for user in collection.find():
        '''
        groups_keys = [key for key in user['passwords'].keys()]
    
        for group_key in groups_keys:
            passwords_keys = [key for key in user['passwords'][group_key].keys()]
    
            for password_key in passwords_keys:
                encrypted_password = _encrypt(user['passwords'][group_key][password_key], public_key)
    
                user['passwords'][group_key][password_key] = encrypted_password
        for group_key in user['passwords'].keys():
            for password_key in user['passwords'][group_key].keys():
                print(_decrypt(user['passwords'][group_key][password_key], private_key))

        collection.update_one({'_id': user['_id']}, {'$set': {'passwords': user['passwords']}})
        '''

    # collection.update_one({'_id': user['_id']}, {'$set': {'generation-settings': user['generation-settings']}})
    # collection.update_one({'_id': user['_id']}, {'$set': {'tmp': user['tmp']}})
    # collection.update_one({'_id': user['_id']}, {'$unset': {'generation_settings': ''}})
    # collection.update_one({'_id': i['_id']}, {'$set': {'tmp_password_title': ''}})
    # collection.update_one({'_id': i['_id']}, {'$set': {'generation_settings': {'len': 12, 'alphabet': 'def'}}})
