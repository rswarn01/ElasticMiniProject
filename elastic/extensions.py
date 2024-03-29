import logging
from flask_sqlalchemy import SQLAlchemy as _BaseSQLAlchemy
from flask_marshmallow import Marshmallow
from flask_caching import Cache
from flask_cors import CORS
from flask_praetorian import Praetorian
from flask_migrate import Migrate
from elastic.utils.flask_azure import FlaskAzure
from elasticsearch import Elasticsearch
from flask import current_app as app
from elastic.utils.flask_azure import FlaskAzure
from elastic.utils.flask_snowflake import FlaskSnowflake


class SQLAlchemy(_BaseSQLAlchemy):
    def apply_pool_defaults(self, app, options):
        super(SQLAlchemy, self).apply_pool_defaults(app, options)
        options["pool_pre_ping"] = True
        return options


db = SQLAlchemy()
mm = Marshmallow()
cache = Cache()
guard = Praetorian()
azure = FlaskAzure()
snowflake = FlaskSnowflake()


CERT_FINGERPRINT = "4561c3a1c4395b3bfdb56c794e5cb644451afb9551ab1b8fe0257d0ae383e29b"
ELASTIC_USER = "elastic"
ELASTIC_SECRET = "4WiXuTF_3bs7FlA0_vSB"

es = Elasticsearch(
    "https://localhost:9200",
    ssl_assert_fingerprint=CERT_FINGERPRINT,
    http_auth=(ELASTIC_USER, ELASTIC_SECRET),
)


def init_extensions(app):

    # sqlalchecmy
    db.app = app
    db.init_app(app)

    # marshmallow
    mm.init_app(app)
    azure.init_app(app)

    # blob
    azure.init_app(app)

    # snowflake
    snowflake.init_app(app)

    # Flask caching
    try:
        cache.init_app(app)
    except Exception as exc:
        print(f"Cache failed to conn... --->  {exc}")

    # # Monkey Patching Cache function to handle exception at central place
    cache_get = cache.get
    cache_set = cache.set
    cache_clear = cache.clear

    def get_from_cache(key):
        try:
            return cache_get(key)
        except Exception:
            logging.error("Not able to get value from cache - %s", key)
            return None

    def set_to_cache(key, value, timeout):
        try:
            cache_set(key, value, timeout)
            logging.info("Cache set successfully - %s", key)
        except Exception:
            logging.error("Not able to set value in cache - %s", key)

    def clear_cache(**kwargs):
        try:
            cache_clear(**kwargs)
            logging.info("Cache Cleared.")
        except Exception as exc:
            logging.error("Not able to clear cache. Exception : %s" % (exc))

    cache.get = get_from_cache
    cache.set = set_to_cache
    cache.clear = clear_cache

    # # migration
    Migrate(app, db, render_as_batch=False)

    CORS(app, expose_headers=["Content-Disposition"])
