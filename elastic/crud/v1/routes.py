from flask_restx import Namespace, Resource
import flask_praetorian
from . import controllers
from elastic.utils import Response

api = Namespace(
    "data_upload",
    description="data upload routes",
    decorators=[flask_praetorian.auth_required],
)

@api.route("/insert_data")
class InsertDocs(Resource):
    def post(self):
        """insert data to elastic"""
        return controllers.insert()
    
@api.route("/search_data")
class SearchDocs(Resource):
    def get(self):
        """insert data to elastic"""
        return controllers.search()