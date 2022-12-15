from elastic.extensions import mm
from marshmallow import fields
from elastic.models import SupplierMaster, Twits


class SupplierMasterSchema(mm.SQLAlchemyAutoSchema):
    class Meta:
        model = SupplierMaster
        include_fk = True


class TwitterSchema(mm.SQLAlchemyAutoSchema):
    class Meta:
        model = Twits
        include_fk = True
