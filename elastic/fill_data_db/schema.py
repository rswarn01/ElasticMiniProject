from elastic.extensions import mm
from marshmallow import fields

from elastic.models import (
    Twits
)

class TwitsSchema(mm.SQLAlchemyAutoSchema):
    class Meta:
        model = Twits