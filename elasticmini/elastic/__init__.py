from flask import Flask, Blueprint, jsonify, redirect
from flask_restx import Api as RestX_Api
from elastic.models import User
from os import getenv
from elastic.commands import elastic_cli

from elastic import extensions


from elastic.auth.v1 import auth_api_v1

api_blueprint = Blueprint("api", __name__, url_prefix="/api")

authorizations = {
    "JWT Token Authentication": {
        "type": "apiKey",
        "in": "header",
        "name": "Authorization",
        "key": "Bearer xxxx",
    }
}


rest_api = RestX_Api(
    api_blueprint,
    title="elastic",
    version="1.0",
    description="Swagger UI / API specs for Cervello elastic application",
    authorizations=authorizations,
)

rest_api.add_namespace(auth_api_v1, path="/v1/auth")

def create_app():
    """Create the flask app and intialize all the extensions"""

    # flask app
    app = Flask(__name__)

    print("App Created..")

    # register blueprint with application
    app.register_blueprint(api_blueprint)

    # load env specific configs
    app.config.from_object(get_config_object_path())

    # initialize all extensions
    extensions.init_extensions(app)

    # # praetorian (JWT token) intialize
    extensions.guard.init_app(app, User)

    app.cli.add_command(elastic_cli)

    # 404 route handler
    @app.errorhandler(404)
    def route_not_present(err):
        return (
            jsonify(
                {
                    "success": False,
                    "error": {"errorCode": err.code, "message": err.description},
                }
            ),
            404,
        )

    # redirect the root to /api for easy access of swagger docs for devs
    @app.route("/")
    def redirect_to_swagger_spec():
        return redirect("/api")

    @app.shell_context_processor
    def shell_context():  # pylint: disable=unused-variable # pragma: no cover
        """The app.shell_context_processor decorator registers the function as a shell context function.
        When the `flask shell` command runs, it will invoke this function
        and register the items returned by it in the shell session.
        """
        return {"db": extensions.db}

    return app


def get_config_object_path() -> str:
    """reads `FLASK_ENV` from OS and returns string that can be used with app.config.from_object.
    If `FLASK_ENV` not set in OS, returns `elastic.config.DevelopmentConfig`

    Returns:
        str: one of 'elastic.config.DevelopmentConfig', 'elastic.config.TestingConfig', 'elastic.config.ProductionConfig'
    """
    try:
        dev_config = "elastic.config.DevelopmentConfig"
        test_config = "elastic.config.TestingConfig"
        prod_config = "elastic.config.ProductionConfig"

        env = getenv("FLASK_ENV")
        environment_configuration = dev_config

        if env in ["development", "extdev", "dev", "demo"]:
            environment_configuration = dev_config
        elif env == "testing":
            environment_configuration = test_config
        elif env in ["production", "prod", "stage"]:
            environment_configuration = prod_config
    except Exception:
        # logging.error(
        #     "Failed to load FLASK_ENV in application factory. Loading Dev environment configs."
        # )
        environment_configuration = dev_config

    return environment_configuration
