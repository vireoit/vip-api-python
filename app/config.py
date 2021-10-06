import os
from typing import List, Type

basedir = os.path.abspath(os.path.dirname(__file__))



class BaseConfig:
    CONFIG_NAME = "base"
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "InSchola3is@India@123"


class DevelopmentConfig(BaseConfig):
    CONFIG_NAME = "dev"
    DEBUG = True

    DB_NAME = 'inscholaris_database'
    DB_HOST_NAME = '104.197.35.192'
    DB_USER = 'postgres'
    DB_PASSWORD = 'india2121@231'
    DB_PORT = 5432

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'postgres://{username}:{password}@{host}:{port}/{db_name}' \
        .format(username=DB_USER, password=DB_PASSWORD, host=DB_HOST_NAME, port=DB_PORT, db_name=DB_NAME)
    SECRET_KEY = os.getenv(
        "DEV_SECRET_KEY", "You can't see California without Marlon Widgeto's eyes"
    )


EXPORT_CONFIGS: List[Type[BaseConfig]] = [
    DevelopmentConfig
]

config_by_name = {cfg.CONFIG_NAME: cfg for cfg in EXPORT_CONFIGS}

