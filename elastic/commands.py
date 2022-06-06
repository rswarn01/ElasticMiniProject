import logging
from flask.cli import AppGroup, with_appcontext

from elastic.extensions import db, cache


elastic_cli = AppGroup("elastic", help="elasticmarking custom CLI commands")


@elastic_cli.command(name="create_db")
@with_appcontext
def create_db_command():
    """create_db command used to create initial db for the application."""
    db.create_all()


@elastic_cli.command(name="create_database")
def create_database():
    """Create SQL database tables, if not created already."""
    db.create_all()


@elastic_cli.command(name="deploy")
@with_appcontext
def deploy():
    """deploy command used create all necessary tables\
         and insert necessary entries while starting the application.
    """
    # Create Database
    db.create_all()

    try:
        cache.clear()  # To clear the cache while deploying the app
    except Exception as exc:
        logging.info(
            "Failed to clear cache. This happends mostly when connection to Redis could not be established. Exception: %s"
            % (str(exc))
        )
