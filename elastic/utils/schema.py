from marshmallow import fields
import json
from elastic.extensions import mm

from elastic.models import (
    UsageTracking,
    FileDetail,
    Notification,
    UserClientMap,
    CompanyData,
    Client,
)


class CompanyDataSchema(mm.SQLAlchemyAutoSchema):
    class Meta:
        model = CompanyData
        ordered = True

    client_dw_id = mm.auto_field()
    client_id = mm.auto_field()
    industry_grp_id = mm.auto_field()
    revenue = mm.auto_field()
    procurement_fte = mm.auto_field()
    direct_procurement_fte = mm.auto_field()
    indirect_procurement_fte = mm.auto_field()
    uploaded_by = mm.auto_field()
    uploaded_on = mm.auto_field()


company_data_schema = CompanyDataSchema()
company_data_schema_many = CompanyDataSchema(many=True)


class FileDetailSchema(mm.SQLAlchemyAutoSchema):
    class Meta:
        model = FileDetail
        ordered = True

    file_id = mm.auto_field()
    user_id = mm.auto_field()
    client_id = mm.auto_field()
    meta_table_id = mm.auto_field()
    reviewer_id = mm.auto_field()
    file_name = mm.auto_field()
    uri_path = mm.auto_field()
    year = mm.auto_field()
    archived_path = mm.auto_field()
    approved_on = mm.auto_field()
    is_approved = mm.auto_field()
    file_type = mm.auto_field()
    comments = mm.auto_field()
    is_active = mm.auto_field()
    created_date = mm.auto_field()
    modified_date = mm.auto_field()


file_detail_schema = FileDetailSchema()
file_detail_schema_many = FileDetailSchema(many=True)


class UsageTrackingSchema(mm.SQLAlchemyAutoSchema):
    class Meta:
        model = UsageTracking
        ordered = True

    usage_tracking_id = mm.auto_field()
    user_id = mm.auto_field()
    action_id = mm.auto_field()
    file_id = mm.auto_field()
    query_input = fields.Method("process_query_input")
    created_date = mm.auto_field()
    modified_date = mm.auto_field()

    def process_query_input(self, obj, **kwargs):
        if obj.query_input is not None:
            query_input = json.dumps(obj.query_input)
            return query_input
        return obj.query_input


usage_tracking_schema_file = UsageTrackingSchema(many=True)


class NotificationSchema(mm.SQLAlchemyAutoSchema):
    class Meta:
        model = Notification
        ordered = True

    notification_id = mm.auto_field()
    user_id = mm.auto_field()
    usage_tracking_id = mm.auto_field()
    is_read = mm.auto_field()
    notification_message = mm.auto_field()
    scheduled_notification_date = mm.auto_field()
    scheduled_notification_status = mm.auto_field()
    application_name = mm.auto_field()
    created_date = mm.auto_field()
    modified_date = mm.auto_field()


notification_file_schema = NotificationSchema(many=True)


class UserClientMapSchema(mm.SQLAlchemyAutoSchema):
    class Meta:
        model = UserClientMap
        ordered = True

    user_client_map_id = mm.auto_field()
    user_id = mm.auto_field()
    client_id = mm.auto_field()
    is_active = mm.auto_field()
    created_date = mm.auto_field()
    modified_date = mm.auto_field()


user_client_map_schema = UserClientMapSchema(many=True)


class ClientSchema(mm.SQLAlchemyAutoSchema):
    class Meta:
        model = Client
        ordered = True

    client_id = mm.auto_field()
    client_name = mm.auto_field()
    is_active = mm.auto_field()
    is_deleted = mm.auto_field()
    created_date = mm.auto_field()
    modified_date = mm.auto_field()
    deleted_date = mm.auto_field()


client_schema = ClientSchema()
client_schema_many = ClientSchema(many=True)
