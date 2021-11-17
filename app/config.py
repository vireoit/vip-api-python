import os
from typing import List, Type

basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig:
    CONFIG_NAME = "base"
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "super-secret"
    JWT_IDENTITY_CLAIM = "unique_name"
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'vip@tangentia.com'  # enter your email here
    MAIL_DEFAULT_SENDER = 'vip@tangentia.com'  # enter your email here
    MAIL_PASSWORD = 'VipTangentia@2021'


class DevelopmentConfig(BaseConfig):
    CONFIG_NAME = "dev"
    DEBUG = True
    MONGO_DBNAME = "VireoQA"

    MONGO_URI = "mongodb+srv://cycloides:cycloides%40123@vireointegrative.z1tl8.mongodb.net/VireoQA"
    SECRET_KEY = os.getenv(
        "DEV_SECRET_KEY", "You can't see California without Marlon Widgeto's eyes"
    )


class QaConfig(BaseConfig):
    CONFIG_NAME = "test"
    DEBUG = True
    MONGO_DBNAME = "Vireo"

    MONGO_URI = "mongodb+srv://cycloides:cycloides%40123@vireointegrative.z1tl8.mongodb.net/Vireo"
    SECRET_KEY = os.getenv(
        "DEV_SECRET_KEY", "You can't see California without Marlon Widgeto's eyes"
    )

EXPORT_CONFIGS: List[Type[BaseConfig]] = [
    DevelopmentConfig, QaConfig
]

config_by_name = {cfg.CONFIG_NAME: cfg for cfg in EXPORT_CONFIGS}

