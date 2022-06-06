from flask_restx import Namespace, Resource, reqparse
import flask_praetorian
from . import controllers
from flask import request
from elastic.utils import Response

api = Namespace(
    "data_load",
    description="data load routes",
    decorators=[flask_praetorian.auth_required],
)

@api.route("/load_large_data")
class LoadLargeData(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        input_sheet = request.files.get("sheet", None)
        if not input_sheet:
            return Response.failure(
                400,
                "Input payload validation failed",
                payload={"sheet": "Missing required parameter in the post body"},
            )
        args = parser.parse_args()
        return controllers.load_data_into_db(input_sheet)