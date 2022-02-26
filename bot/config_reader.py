import configparser
from dataclasses import dataclass


@dataclass
class HelperBot:
    token: str
    cluster_link: str


@dataclass
class Config:
    helper_bot: HelperBot


def load_config(path: str):
    config = configparser.ConfigParser()
    config.read(path)

    helper_bot = config["helper_bot"]

    return Config(
        helper_bot=HelperBot(
            token=helper_bot["token"],
            cluster_link=helper_bot["MongoDBClusterLink"]
        )
    )
