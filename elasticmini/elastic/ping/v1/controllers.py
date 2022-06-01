from flask import jsonify

from elastic.extensions import db

from ..models import Ping, ping_marshal


# @cache.memoize(timeout=60)
def get_ping():
    """Get ping from server

    Returns:
        str : reply from server
    """
    ping = Ping.query.first()
    return ping_marshal.dump(ping)


def create_ping_cache_key(f, *args):
    key = "ping_custom_key_"
    for item in args:
        key += str(item)
    return key


get_ping.create_cache_key = create_ping_cache_key


def add_ping(value):
    """Add ping to sql db

    Args:
        value (str): any str value

    Returns:
        str: add ping status
    """
    ping = Ping(value=value)
    try:
        db.session.add(ping)
        db.session.commit()
    except Exception as exc:
        return jsonify({"msg": "Add ping failed", "error": str(exc)})
    return jsonify("Ping added successfully")


def get_all_from_snowflake():
    """get records from snowflake"""
    query = f"SELECT TO_JSON(ARRAY_AGG(object_construct(*))) FROM USER"
    try:
        return
    # Snowflake not in use
    # result = snowflake.execute(query).fetchall()
    except Exception as exc:
        return "Failed to get data" + str(exc)
    # return result


def insert_to_snowflake(args):
    """insert records to snowflake"""
    try:
        # Snowflake not in use
        pass
        # snowflake.execute(
        #     f"INSERT INTO USER VALUES {args.get('first_name'),args.get('last_name')}"
        # )
    except Exception as exc:
        return "Error occured " + str(exc), 400
    return "Record added successfully"


AZURE_BASE_PATH = "demo/"
