from flask_restx import Namespace, Resource, reqparse
from flask import request
from . import controllers
from elastic.utils import Response

api = Namespace(
    "data_upload",
    description="data upload routes",
)

@api.route("/insert_data")
class InsertDocs(Resource):
    def post(self):
        """insert data to elastic"""
        return controllers.insert()
    
@api.route("/search_data")
class SearchDocs(Resource):
    def get(self):
        """search data to elastic"""
        
        parser = reqparse.RequestParser()
        parser.add_argument(
            "searching_data", type=str, nullable=False, required=False, location="args"
        )
        args = parser.parse_args()
        return controllers.search(args)
    
@api.route("/insert_bulk_data")
class InsertBulkDocs(Resource):
    def post(self):
        input_sheet = request.files.get("sheet", None)
        if not input_sheet:
            return Response.failure(
                400,
                "Input payload validation failed",
                payload={"sheet": "Missing required parameter in the post body"},
            )
        return controllers.insert_bulk_data(input_sheet)