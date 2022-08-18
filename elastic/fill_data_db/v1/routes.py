from flask_restx import Namespace, Resource, reqparse
import flask_praetorian
from . import controllers
from flask import request
from elastic.utils import Response

api = Namespace(
    "data_load",
    description="data load routes",
)

@api.route("/load_large_data")
class LoadLargeData(Resource):
    def post(self):
        input_sheet = request.files.get("sheet", None)
        if not input_sheet:
            return Response.failure(
                400,
                "Input payload validation failed",
                payload={"sheet": "Missing required parameter in the post body"},
            )
        return controllers.load_data_into_db(input_sheet)
    
@api.route("/search_data")
class SearchSupplier(Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument(
            "searching_data", type=str, nullable=False, required=False, location="args"
        )
        args = parser.parse_args()
        return controllers.search_data_from_db(args)