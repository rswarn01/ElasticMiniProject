from elastic.extensions import mm
from marshmallow import fields
from elastic.models import SupplierMaster

class SupplierMasterSchema(mm.SQLAlchemyAutoSchema):
    class Meta:
        model = SupplierMaster
        include_fk = True