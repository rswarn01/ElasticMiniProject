"""Snowflake wrapper package.

Wraps the original `snowflake.connector` object \
to provide a clean interface for accessing Snowflake DB.
This wrapper directly takes env variables from current app config.
"""
import logging

from flask import _app_ctx_stack
import snowflake.connector
import sqlalchemy.pool as pool


class FlaskSnowflake:
    """Wrapper Class for `snowflake.connector` object \
        that serves as interface between actual `snowflake` package and the app.
    """

    def __init__(self, app=None):
        self.app = app
        self.conn_pool = None

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """Intialize snowflake wrapper

        Args:
            app (flask app)
        """
        app.config.setdefault("SNOWFLAKE_USER", None)
        app.config.setdefault("SNOWFLAKE_ACCOUNT_NAME", None)
        app.config.setdefault("SNOWFLAKE_ACCOUNT_PASSWORD", None)
        app.config.setdefault("SNOWFLAKE_WAREHOUSE", None)
        app.config.setdefault("SNOWFLAKE_DATABASE", None)
        app.config.setdefault("SNOWFLAKE_SCHEMA", None)
        app.config.setdefault("SNOWFLAKE_ROLE", None)

        # store the application object for accessing configuration while creation snowflake conenction
        if app and not self.app:
            self.app = app

        try:
            self.conn_pool = self.get_pool()
        except Exception as error:
            logging.warning(
                "Exception in create connection Pool while Extention initialisation. Error: %s",
                str(error),
            )

        # After every request is over, close the connection
        app.teardown_appcontext(self.close_connection_on_teardown)
        logging.info("Snowflake Empty Pool created on Extention initialisation")

    def close_connection_on_teardown(self, exception):
        """Close snowflake connection (if present in current app context) \
             after request is destructured.
        """
        if exception:
            logging.warning(
                "flake_snowflake: Caught an exception while app context teardown. Error: %s",
                exception,
            )

        ctx = _app_ctx_stack.top
        if hasattr(ctx, "snowflake_connection_for_request"):
            try:
                logging.info("Closing Connection object found in app context")
                ctx.snowflake_connection_for_request.close()
            except Exception as exc:
                logging.warning(
                    "Error in closing connection while app context teardown. Error: %s",
                    exc,
                )

    def create_connection(self):
        """Returns a snowflake connection object.
        This function is utiised by the snowflake.pool.QueuePool \
            as a connection creator when required.

        This makes use of application instance stored, \
            hence not adept for multiple application settings.

        Returns:
            snowflake.connector: Snowflake connection
        """
        return snowflake.connector.connect(
            user=self.app.config.get("SNOWFLAKE_USER"),
            password=self.app.config.get("SNOWFLAKE_ACCOUNT_PASSWORD"),
            account=self.app.config.get("SNOWFLAKE_ACCOUNT_NAME"),
            warehouse=self.app.config.get("SNOWFLAKE_WAREHOUSE"),
            database=self.app.config.get("SNOWFLAKE_DATABASE"),
            schema=self.app.config.get("SNOWFLAKE_SCHEMA"),
            role=self.app.config.get("SNOWFLAKE_ROLE"),
            client_session_keepalive=True,
        )

    def get_pool(self):
        """Create a connection pool and returns.
            Ideally, should be called ONLY at initialisation stage.
            But can be called multiple times to get multiple Pools.

        Returns:
            snowflake.pool.QueuePool: Connection Pool Object
        """
        logging.info("Creating a new Connection Pool.")
        return pool.QueuePool(self.create_connection, echo=True)

    @property
    def current_pool(self):
        """Returns the SQL Alchemy connection pool.
        Ideally, should always return the same connection pool \
            (that is: self.conn_pool) created at the initialisation of this wrapper.
        If connection pool is Null ( Due to some exception ), creates a new connection and retrrns.

        Returns:
            [sqlalchemy.pool.QueuePool]: Connection Pool Object
        """
        if not self.conn_pool:
            logging.warning(
                "Current Pool not available (Ideally, should never happen). Creating a new pool and returning."
            )
            self.conn_pool = self.get_pool()
        return self.conn_pool

    @property
    def connection_from_pool(self):
        """Returns a snowflake connection from the pool, \
            that gets closed on the application context teardown.

            Stores the connection on the context and If called multiple times\
                in same request cycle, returns the same snowflake connection.
        ```py
            query = "SELECT * FROM USER"
            connection = snowflake.connection_from_pool
            result = connection.cursor().execute(query)
            connection.close()
        ```
        Returns:
            [SnowflakeConnection]: instance of class:SnowflakeConnection
        """

        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, "snowflake_connection_for_request"):
                ctx.snowflake_connection_for_request = self.current_pool.connect()
                logging.info(
                    "Snowflake connection found in app context, returning the same connection."
                )
            return ctx.snowflake_connection_for_request
        else:
            logging.warning("Connection from Pool requested without App Context.")

    def execute(self, query: str):
        """Execute query on cursor by taking a snowflake connection from the Pool.

        Args:
            query (str): Snowflake Query to Execute on snowflake
        """
        ctx = _app_ctx_stack.top
        for i in range(5):
            try:
                if ctx is not None:
                    logging.info("Started running snowflake query!")
                    print("Started running snowflake query!")
                    return self.connection_from_pool.cursor(
                        snowflake.connector.DictCursor
                    ).execute(query)
            except Exception as exc:
                logging.info("Failed to run snowflake query!")
                print("Failed to run snowflake query!", str(exc))
        else:
            logging.warning("Execute called without App Context.")
