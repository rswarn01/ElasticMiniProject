from flask_restx import Namespace, Resource, reqparse
from flask import request
from . import controllers
from elastic.utils import Response

api = Namespace(
    "crud-operations",
    description="data upload routes",
)


@api.route("/insert_data")
class InsertDocs(Resource):
    def post(self):
        """insert data to elastic"""
        return controllers.insert()


@api.route("/search_data")
class SearchDocs(Resource):
    def post(self):
        """search data to elastic"""

        parser = reqparse.RequestParser()
        parser.add_argument("searching_data", type=str, location="form")
        args = parser.parse_args()
        return controllers.search(args)


@api.route("/search_twitter_data")
class SearchTwitterDocs(Resource):
    def post(self):
        """search data to elastic"""

        parser = reqparse.RequestParser()
        parser.add_argument("searching_data", type=str, location="form")
        args = parser.parse_args()
        return controllers.search_twitter(args)


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


@api.route("/delete_index")
class DeleteIndex(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("index", type=str, location="form")
        args = parser.parse_args()
        return controllers.delete_index(args)


@api.route("/insert_supplier_data")
class InsertSupplierData(Resource):
    def post(self):
        input_sheet = request.files.get("sheet", None)
        if not input_sheet:
            return Response.failure(
                400,
                "Input payload validation failed",
                payload={"sheet": "Missing required parameter in the post body"},
            )
        return controllers.add_new_suppliers_generate_ingest_file(input_sheet)


@api.route("/insert_supplier_additional_attribute_data")
class InsertSupplierAdditionalAttributeData(Resource):
    def post(self):
        input_sheet = request.files.get("sheet", None)
        if not input_sheet:
            return Response.failure(
                400,
                "Input payload validation failed",
                payload={"sheet": "Missing required parameter in the post body"},
            )
        return controllers.fill_additional_attribute(input_sheet)


@api.route("/create_new_dummy_index")
class CreateDummyIndex(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("index", type=str, location="form")
        args = parser.parse_args()
        return controllers.create_new_index_dummy(args)


@api.route("/update_documents")
class UpdateDocument(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("searching_data", type=str, location="form")
        args = parser.parse_args()
        return controllers.update_delete_document(args)


@api.route("/update_db_and_sync_elastic")
class UpdateDbandSyncElastic(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("supplier_metadata_id", type=int, location="form")
        parser.add_argument("supplier_id", type=int, location="form")
        parser.add_argument("supplier_name", type=str, location="form")
        parser.add_argument("new_value", type=str, location="form")
        args = parser.parse_args()
        return controllers.sync_db_and_elastic(args)
