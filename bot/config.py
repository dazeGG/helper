from pymongo import MongoClient

from bot.config_reader import load_config


config = load_config("config/bot.ini")
collection = MongoClient(config.helper_bot.cluster_link)['test']['users']
