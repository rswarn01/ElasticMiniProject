"""Environment Specific Config Values should be set here
    """

import os
from urllib.parse import quote_plus as urlquote
from dotenv import load_dotenv
from apscheduler.executors.pool import ProcessPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

load_dotenv()


BASE_DIR = os.path.abspath(os.path.dirname(__name__))
TRUTHY_VALUES = ["True", True, "true", "1", 1, "yes", "Yes", "Y", "y"]


class BaseConfig(object):
    # Flask variables
    DEBUG = False
    TESTING = False

    PROTOCOL = "https://"

    # Application variables
    APP_BASE_URL = PROTOCOL + os.getenv("APP_BASE_URL")
    SECRET_KEY = os.getenv("APP_VALIDATION_KEY") or os.urandom(15).hex()

    # sql db specific
    APP_DB_USER = os.getenv("APP_DB_USER")
    APP_DB_SECRET = os.getenv("APP_DB_SECRET")
    APP_DB_HOST = os.getenv("APP_DB_HOST")
    APP_DB_PORT = os.getenv("APP_DB_PORT")
    APP_DB_NAME = os.getenv("APP_DB_NAME")
    APP_DB_USE_SSL = os.getenv("APP_DB_USE_SSL", "False") in TRUTHY_VALUES

    # Flask-Mail related variables
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_SENDER")
    MAIL_SENDGRID_API_KEY = os.getenv("MAIL_SENDGRID_API_KEY")

    # SQLALCHEMY_DATABASE_URI = (
    #     f"mssql+pymssql://{APP_DB_USER}:%s@{APP_DB_HOST}:{APP_DB_PORT}/{APP_DB_NAME}"
    #     % urlquote(APP_DB_SECRET)
    # )
    SQLALCHEMY_DATABASE_URI = "mssql+pymssql://sa:Password12345@localhost/elasticdb"

    # to disable logs of sqlalchemy
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = (
        os.getenv("APP_DB_TRACK_MODIFICATIONS", "False") in TRUTHY_VALUES
    )

    # flask-caching variables
    CACHE_TYPE = os.getenv("CACHE_TYPE", "null")
    CACHE_REDIS_HOST = os.getenv("CACHE_HOST")
    CACHE_REDIS_PORT = os.getenv("CACHE_PORT")
    CACHE_REDIS_DB = os.getenv("CACHE_DB")
    CACHE_REDIS_PASSWORD = os.getenv("CACHE_SECRET")
    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_TIMEOUT", "120"))

    # Flask-Mail related variables
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_SENDER")
    MAIL_SUBJECT_PREFIX = os.getenv("MAIL_SUBJECT_PREFIX")
    MAIL_SERVER = os.getenv("MAIL_HOST")
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_SECRET")
    MAIL_PORT = os.getenv("MAIL_PORT")
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL", "True") in TRUTHY_VALUES
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS", "False") in TRUTHY_VALUES
    MAIL_SENDGRID_API_KEY = os.getenv("MAIL_SENDGRID_API_KEY")

    # flask-praetorian variables
    # JWT_ACCESS_LIFESPAN = {"minutes": int(os.environ.get("ACCESS_TOKEN_EXPIRY_MINS"))}
    # JWT_REFRESH_LIFESPAN = {"minutes": int(os.environ.get("REFRESH_TOKEN_EXPIRY_MINS"))}
    # JWT_REGISTRATION_LIFESPAN = (
    #     f"""{int(os.environ.get("REGISTRATION_TOKEN_EXPIRY_DAYS"))} days"""
    # )

    # azure AD variables
    AZURE_OAUTH_CLIENT_ID = os.getenv("AZURE_OAUTH_CLIENT_ID")
    AZURE_OAUTH_CLIENT_SECRET = os.getenv("AZURE_OAUTH_CLIENT_SECRET")
    AZURE_OAUTH_TENANT_NAME = os.getenv("AZURE_OAUTH_TENANT_ID", "common")
    AUTHORITY = "https://login.microsoftonline.com/" + AZURE_OAUTH_TENANT_NAME
    ENDPOINT = os.getenv("AZURE_OAUTH_ENDPOINT")
    IMAGE_ENDPOINT = os.getenv("AZURE_OAUTH_IMAGE")
    SCOPE = os.getenv("AZURE_OAUTH_SCOPE")
    STORAGE_TOKEN_EXPIRY_MINUTES = int(os.getenv("STORAGE_TOKEN_EXPIRY_MINUTES", "60"))
    APP_ENV = os.environ.get("APP_ENV")

    # azure blob
    AZURE_STORAGE_CONNECTION_STRING = os.environ.get("STORAGE_CONNECTION_STRING")
    AZURE_STORAGE_CONTAINER_NAME = os.environ.get("STORAGE_CONTAINER_NAME")

    # Snowflake connection
    SNOWFLAKE_USER = os.environ.get("SNOWFLAKE_USER")
    SNOWFLAKE_ACCOUNT_NAME = os.environ.get("SNOWFLAKE_ACCOUNT_NAME")
    SNOWFLAKE_ACCOUNT_PASSWORD = os.environ.get("SNOWFLAKE_SECRET")
    SNOWFLAKE_WAREHOUSE = os.environ.get("SNOWFLAKE_WAREHOUSE")
    SNOWFLAKE_DATABASE = os.environ.get("SNOWFLAKE_DATABASE")
    SNOWFLAKE_SCHEMA = os.environ.get("SNOWFLAKE_SCHEMA")
    SNOWFLAKE_ROLE = os.environ.get("SNOWFLAKE_ROLE")

    SCHEDULER_TIMEZONE = os.environ.get("SCHEDULER_TIMEZONE")
    SCHEDULER_JOBSTORES = {"default": SQLAlchemyJobStore(url=SQLALCHEMY_DATABASE_URI)}
    SCHEDULER_API_PREFIX = "/api/scheduler"
    SCHEDULER_ENDPOINT_PREFIX = "api.scheduler."
    APP_ENV = os.environ.get("APP_ENV")
    # EMAIL_SCHEDULED_PERIOD = int(os.getenv("SCHEDULED_EMAIL_DAYS", "90"))


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = False
    SCHEDULER_API_ENABLED = True

    # print sql logs for development
    SQLALCHEMY_ECHO = False


class TestingConfig(BaseConfig):
    TESTING = True


class ProductionConfig(BaseConfig):
    pass
