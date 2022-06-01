"""Utilities related to Redis
"""
import logging
import os
import redis

from elastic.extensions import cache

# These variables are used only in case of native redis functions.
# app.config is not used here to make the native redis functions independent of app.
CACHE_TYPE = os.getenv("CACHE_TYPE", default="null")
REDIS_HOST = os.getenv("CACHE_HOST", default="127.0.0.1")
REDIS_PORT = int(os.getenv("CACHE_PORT", default="6379"))
REDIS_DB = int(os.getenv("CACHE_DB", default="0"))
REDIS_PASSWORD = os.getenv("CACHE_SECRET", "")

# Common Redis Client


def _new_redis_client():
    """Returns a new redis client."""
    return redis.Redis(
        host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, password=REDIS_PASSWORD
    )


_redis_client = _new_redis_client()


def get_redis_client():
    """Returns a redis client. If connection error, re-connects and return."""
    global _redis_client

    try:
        _redis_client.ping()
    except Exception as err:  # pylint: disable=broad-except
        # set the connection again on error
        _redis_client = _new_redis_client()
        logging.warning(
            "Failed to Ping redis. Will create a new client. Error %s", str(err)
        )

    return _redis_client


def clear_all():
    """Clear all the keys from Redis.
    Uses object from flask_caching,
    """
    return cache.clear()


def clear_all_native():
    """Clear all the keys from Redis.
    Makes a separate connetion to redis. Does NOT uses object form flask_caching
    """
    status = False

    if CACHE_TYPE == "null":
        return status

    redis_client = get_redis_client()

    try:
        status = redis_client.flushdb(asynchronous=True)
    except redis.exceptions.ConnectionError:
        logging.error("ConnectionError - Error while connecting to Redis.")
    except Exception:  # pylint: disable=broad-except
        logging.exception("clear_all_native: Error while flushing redis db")

    return status


def delete_pattern(pattern: str) -> bool:
    """Searches, Deletes keys in Redis that match the regex pattern. `CACHE_KEY_PREFIX` is prefixed before the pattern to search.
    Uses the redis object form flask_caching

    Args:
        pattern (str): searches redis keys for this pattern

    Returns:
        bool: True if match found and deleted, False otherwise
    """
    search_pattern = "flask_cache_*" + pattern + "*"
    logging.debug("Searching Redis for pattern: %s", search_pattern)

    status = False
    try:
        bkeys = cache.cache._read_clients.keys(search_pattern)
        keys = [k.decode("utf-8", errors="ignore") for k in bkeys if k]
        if keys:
            status = cache.cache._write_client.delete(*keys)
    except redis.exceptions.ConnectionError:
        logging.error("ConnectionError Error while searching key from Redis.")
    except Exception:  # pylint: disable=broad-except
        logging.exception(
            "Error while searching / deleting keys from Redis. Pattern: %s", pattern
        )
    # return the response as False if Exception occured or match not found. True otherwise.
    return status


def delete_pattern_native(pattern: str) -> int:
    """Searches, Deletes keys in Redis that match the regex pattern. `CACHE_KEY_PREFIX` is **NOT** prefixed before the pattern for search.
    Makes a separate connetion to redis. Does NOT uses object form flask_caching

    Args:
        pattern (str): searches redis keys for this pattern

    Returns:
        int: True if match found and deleted, False otherwise
    """

    if CACHE_TYPE == "null":
        return 0

    def _clear_pattern(_pattern: str) -> int:
        """Remove all keys matching pattern."""
        count = 0

        redis_client = get_redis_client()

        try:
            match = redis_client.scan_iter(pattern)
            for key in match:
                redis_client.delete(key)
                count += 1
        except redis.exceptions.ConnectionError:
            logging.error(
                "clear_pattern_safe - delete_pattern : ConnectionError - Error while connecting to Redis."
            )
        except Exception:  # pylint: disable=broad-except
            logging.exception(
                "clear_pattern_safe - delete_pattern : Error while searching/ deleting keys from Redis. Pattern: %s",
                _pattern,
            )

        return count

    return _clear_pattern(pattern)


def check_redis():
    try:
        _redis_client.ping()
        return False
    except Exception as exc:
        logging.error("No redis connection could be made")
        return True
