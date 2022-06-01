from flask import request
from flask_restx import Resource, Namespace, fields
from elastic.ping.v1 import controllers

api = Namespace("Ping", description="API to ping the server")

snowflake_request_model = api.model(
    "Snowflake post request",
    {
        "first_name": fields.String(description="name of person", required=True),
        "last_name": fields.String(description="last name of person", required=True),
    },
)


@api.route("/ping")
class Ping(Resource):
    """
    API check
    """

    def get(self):
        """Get ping from server"""
        return controllers.get_ping()

    def post(self):
        value = request.get_json().get("value")
        return controllers.add_ping(value)
