import os
from typing import List, Type

basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    CONFIG_NAME = "base"
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "{2FBA4000-290B-4F0B-AF53-3A2AD3C08DDD}"


class DevelopmentConfig(BaseConfig):
    CONFIG_NAME = "dev"
    DEBUG = True
    MONGO_DBNAME = "VireoQA"

    MONGO_URI = "mongodb+srv://cycloides:cycloides%40123@vireointegrative.z1tl8.mongodb.net/VireoQA"
    SECRET_KEY = os.getenv(
        "DEV_SECRET_KEY", "You can't see California without Marlon Widgeto's eyes"
    )


EXPORT_CONFIGS: List[Type[BaseConfig]] = [
    DevelopmentConfig
]

config_by_name = {cfg.CONFIG_NAME: cfg for cfg in EXPORT_CONFIGS}

