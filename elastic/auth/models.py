from elastic.extensions import mm
from elastic.models import Role, User
from marshmallow import fields


class RoleSchema(mm.SQLAlchemyAutoSchema):
    class Meta:
        model = Role


class UserSchema(mm.SQLAlchemySchema):
    role = fields.Nested(RoleSchema, attribute="role")

    class Meta:
        model = User

    user_id = mm.auto_field()
    first_name = mm.auto_field()
    last_name = mm.auto_field()
    email_address = mm.auto_field()
    # user = mm.auto_field()
    # role_name = fields.String(data_key="roles")
    # is_approved = fields.Boolean()
    # is_email_verified = fields.Boolean()
    permissions = fields.List(fields.String())


user_schema = UserSchema()


class UserOrderedSchema(mm.SQLAlchemySchema):
    class Meta:
        model = User
        ordered = True

    user_id = mm.auto_field()
    role_id = mm.auto_field()
    first_name = mm.auto_field()
    last_name = mm.auto_field()
    password = mm.auto_field()
    email_address = mm.auto_field()
    is_active = mm.auto_field()
    created_date = fields.DateTime(attribute="created_date")
    modified_date = fields.DateTime(attribute="updated_date")


user_ordered_schema = UserOrderedSchema()
