from datetime import datetime
from flask import Markup

NORMALIZED_UPLOAD_DATA_CACHE_KEY = "all_data_recieved_cache_key"
XLSX_MIMETYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
TXT_MIMETYPE = "text/plain"
PBIX_MIMETYPE = "application/zip"
PDF_MIMETYPE = "application/pdf"
ACTION_ID_CACHE_KEY = "ACTION_ID_{0}_CACHE_KEY"
ACTION_NAME_CACHE_KEY = "ACTION_NAME_{0}_CACHE_KEY"
AZURE_SEED_FILE = [
    "action",
    "permissions",
    "role",
    "role_permission_map",
    "industry_group_master",
    "category_level",
    "category_tree",
    "module",
    "meta_table",
    "meta_column",
    "region_master",
    "country",
    "client",
    "company_data",
    "file_detail",
]

AZURE_SEED_FOLDER = "seed"
SPEND = "spend"
SAVINGS = "savings"
PRICE = "price"
AZURE_RAW_TEMPLATE_PATH = {
    SPEND: "base_template/raw/spend_raw.xlsx",
    SAVINGS: "base_template/raw/savings_raw.xlsx",
    PRICE: "base_template/raw/price_raw.xlsx",
}


SNOWFLAKE_SPEND_FILTER_VIEW_NAME = "SLIDER_FILTER"
NORMALIZED_AZURE_BASE_PATH = "/templates/harmonized/{0}/"
RAW_AZURE_BASE_PATH = "/templates/raw/{0}/"

HARMONIZED_DIRNAME = "harmonized"
ALL_SEED_USERS = ["benchmarking_admin@kearney.com", "elasticmarking_user@kearney.com"]
AUTHENTICATION_OR_AUTHORIZATION_FAILURE = "AuthenticationError"
TEXT_CSV_CONST = "text/csv"
CSV_EXTENSION = ".csv"

DATA_DISTINCT_DIR = "ingest/data_distinct/"
DATA_DISTINCT_FILE_MAP_DIR = "ingest/data_distinct_file_map/"
SP_DATA_DISTINCT = "SP_DATA_DISTINCT"
SP_DATA_DISTINCT_FILE_MAP = "SP_DATA_DISTINCT_FILE_MAP"

SP_NOTIFICATION = "SP_NOTIFICATION"
CATEGORY_DIR = "ingest/category/"
SP_USERS = "SP_USERS"
USER_DIR = "ingest/users/"
SP_USER_CLIENT_MAP = "SP_USER_CLIENT_MAP"
USER_CLIENT_MAP_DIR = "ingest/user_client_map/"
SP_FILE_DETAIL = "SP_FILE_DETAIL"
SP_COMPANY_DATA = "SP_COMPANY_DATA"
FILE_DETAIL_DIR = "ingest/file_detail/"
COMPANY_DATA_DIR = "ingest/company_data/"
CLIENT_DIR = "ingest/client/"
SP_CLIENT = "SP_CLIENT"
BENCHMARK_HARMONIZED_DIR = "ingest/benchmark_harmonized/"
SP_BENCHMARK_HARMONIZED = "SP_BENCHMARK_HARMONIZED"
SP_PURGE_CLIENT_DATA = "SP_PURGE_CLIENT_DATA"

REQUIRED_FIELDS = {"first_name", "last_name", "email", "role", "is_approved"}

RECEIVER_EMAIL = ["kpssupport@kearney.com"]
FEEDBACK_SUBJECT = "Feedback"
TEMPLATES = "new"
CLIENT_DELETE_SUBJECT = "Client Deleted."

CREATE_ADMIN_SUBJECT = "Admin created"
REMOVE_ADMIN_SUBJECT = "Admin removed"

AZURE_BASE_PATH_ATTACHMENTS = "/attachments/"

SNOWFLAKE_PERSIST_SCHEMA = "PERSIST"

ARCHIVE_PATH = "archive/"
INGEST_PATH = "ingest/"

ENTITY_VIEW_NAME = "entity_vw"
DEFAULT_ENTITY_NAME = "KPS bench Assets"
DEFAULT_ENTITY_TYPE = "global"

STATUS_PREVIEW = "Preview"
STATUS_LATEST = "Latest"
STATUS_ARCHIVED = "Archived"
STATUS_REJECTED = "Rejected"
AZURE_PREVIEW_FILES_PATH = "entities"

SNOWFLAKE_VIEW_NAME = "BENCHMARK_HARMONIZED_V"
SNOWFLAKE_FRAGMENTATION_VIEW_NAME = "SUPPLIER_FRAGMENTATION"


PROCUREMENT_FTES = ["Direct", "Indirect", "All"]
REVIEWED = ["Yes", "No", "All"]
CURRENCY = ["Dollar ($)", "Euro (€)", "Pound (£)"]

PROCUREMENT_FTES_FILTER_MAP = {
    "direct": "DIRECT_PROCUREMENT_FTE",
    "indirect": "INDIRECT_PROCUREMENT_FTE",
    "all_ftes": "PROCUREMENT_FTE",
}

REVIEWED_FILETER_MAP = {"yes": True, "no": False}


def get_url_for_files(entity_id, current_user_id, file_extension):
    return f"{AZURE_PREVIEW_FILES_PATH}/{str(entity_id)}/{entity_id}_{current_user_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}.{file_extension}"


PASSWORD_EXPIRED = Markup(
    """
        <p style="font-size: 30px;line-height: 1.3;color: #000000;font-weight: 600;padding: 0;margin: 0">
            Your password has expired
        </p>
    """
)
ACCOUNT_CREATED = Markup(
    """
        <p  style="font-size: 30px;line-height: 1.3;font-weight: 600;padding: 0;margin: 0;color: #04BB46"">
            Account created successfully
        </p>
    """
)
ACCOUNT_APPROVED = Markup(
    """
        <p  style="font-size: 30px;line-height: 1.3;font-weight: 600;padding: 0;margin: 0;color: #04BB46"">
            Account approved
        </p>
    """
)
WAITING_ACCOUNT_APPROVAL = Markup(
    """
        <p  style="font-size: 30px;line-height: 1.3;font-weight: 600;padding: 0;margin: 0;color: #04BB46"">
            Account Waiting For Approval
        </p>
    """
)
PASSWORD_EXPIRY_DAYS = Markup(
    """
        <p  style="font-size: 30px;line-height: 1.3;color: #000000;font-weight: 600;padding: 0;margin: 0;">
            Your password will expire in <span style="color:#FF3429">{0}</span> days.
        </p>
    """
)
FORGOT_PASSWORD = Markup(
    """
        <p  style="font-size: 30px;line-height: 1.3;color: #000000;font-weight: 600;padding: 0;margin: 0;">
            Forgot password ?
        </p>
    """
)
PASSWORD_CHANGE_MESSAGE = (
    "Please use this below link to create new password for you account."
)
ACCOUNT_CREATION_MESSAGE = "Please use this below link to verify your account."
ACCOUNT_APPROVAL_MESSAGE = "You may log in to the application."
WAITING_ACCOUNT_APPROVAL_MESSAGE = (
    "User has created an account and is waiting for approval - {0}"
)
VERIFY_BUTTON = "Verify Account"
CHANGE_PASSWORD = "Change Password"
VISIT_bench_BUTTON = "Visit bench"
IDENTITY_LINK = "/{0}?token={1}&type={2}"
REDIRECT_PAGE_LINK = "/{0}"
REDIRECT_PARAM = "?preview={0}"

ACCOUNT_CREATION_SUBJECT = "Verify Account"
FORGOT_PASSWORD_SUBJECT = "Change Password"
ACCOUNT_APPROVAL_SUBJECT = "Account Approved"
WAITING_ACCOUNT_APPROVAL_SUBJECT = "Waiting Account Approved"
MAIL_TYPE_REGISTRATION = "registration"
MAIL_TYPE_FORGOT_PASSWORD = "forgot_password"
MAIL_TYPE_PASSWORD_EXPIRY = "password_expiry"
MAIL_TYPE_ADMIN_REGISTRATION = "admin_registration"
MAIL_TYPE_ACCOUNT_APPROVAL = "account_approval"
MAIL_TYPE_WAITING_ACCOUNT_APPROVAL = "waiting_account_approval"
MAIL_TYPE_PREVIEW_ENTITY_PAGE = "preview_entity_page"
REDIRECT_PAGE_PASSWORD = "forgot-password"
REDIRECT_PAGE_VERIFY = "create-account"
VERIFICATION_CODE_SUBJECT = "Two-Factor Authentication"
KEARNEY_DOMAINS = ["kearney.com", "mycervello.com", "atkearney.com"]

CONTENT_EDIT_NOTIFICATION = "{0} has modified content on {1}"
CONTENT_UPLOAD_NOTIFICATION = "Content that you have uploaded is pending approval"
ENTITY_API_ENTITY = "entity"
ENTITY_API_client_data = "client_data"
ENTITY_TYPE_API = "api"
CONTENT_EDIT_SUBJECT = "Content Waiting Approval"
CONTENT_UPLOAD_SUBJECT = "Content Uploaded Successfully"
CONTENT_APPROVAL_SUBJECT = "Uploaded content status changed"
CONTENT_EDIT_HEADING = Markup(
    """
        <p  style="font-size: 30px;line-height: 1.3;color: #000000;font-weight: 600;padding: 0;margin: 0;">
            Content Waiting Approval
        </p>
    """
)
CONTENT_UPLOAD_HEADING = Markup(
    """
        <p  style="font-size: 30px;line-height: 1.3;color: #000000;font-weight: 600;padding: 0;margin: 0;">
            Content Uploaded Successfully
        </p>
    """
)
CONTENT_APPROVAL_HEADING = Markup(
    """
        <p  style="font-size: 30px;line-height: 1.3;color: #000000;font-weight: 600;padding: 0;margin: 0;">
            Uploaded content status changed
        </p>
    """
)
BUTTON_TEXT_ENTITY_PREVIEW = "Go to Preview Page"
BUTTON_TEXT_ENTITY = "Go to Page"
LOGIN_EMAIL_TEMPLATE = "login_email"
CONTENT_APPROVAL_STATUS_NOTIFICATION = "Content that you have uploaded has been {0}"
ENDPOINT_ENTITY = "entity_management"
ENDPOINT_ENTITY_APPROVAL = ENDPOINT_ENTITY + "_approval"
current_timestamp = datetime.utcnow().strftime("%Y%m")

MODULE_ADD_NEW_RECORD_ARCHIVE = "archive/{0}/{1}/{2}"
USAGE_TRACKING_DIR_ARCHIVE = "archive/usage_tracking/{0}/"
DATA_DISTINCT_DIR_ARCHIVE = "archive/data_distinct/{0}/"
CATEGORY_TO_MODULE_MAP_DIR_ARCHIVE = "archive/category_to_module_map/{0}/"
META_TABLE_DIR_ARCHIVE = "archive/meta_table/{0}/"
META_COLUMN_TABLE_DIR_ARCHIVE = "archive/meta_column/{0}/"
SME_CATEGORY_MAP_DIR_ARCHIVE = "archive/sme_category_map/{0}/"
CATEGORY_DIR_ARCHIVE = "archive/category/{0}/"
USER_DIR_ARCHIVE = "archive/users/{0}/"
DATA_DISTINCT_FILE_MAP_DIR_ARCHIVE = "archive/data_distinct_file_map/{0}/"
NOTIFICATION_DIR_ARCHIVE = "archive/notification/{0}/"
USAGE_TRACKING_DIR = "ingest/usage_tracking/"
SP_USAGE_TRACKING = "SP_USAGE_TRACKING"
NOTIFICATION_DIR = "ingest/notification/"
USER_CLIENT_MAP_DIR_ARCHIVE = "archive/user_client_map/{0}/"
FILE_DETAIL_DIR_ARCHIVE = "archive/file_detail/{0}/"
COMPANY_DATA_DIR_ARCHIVE = "archive/company_data/{0}/"
CLIENT_DIR_ARCHIVE = "archive/client/{0}/"


def get_archive_path(file_name=None):
    archive_paths = dict()

    if file_name:
        archive_paths["file_name"] = MODULE_ADD_NEW_RECORD_ARCHIVE.format(
            HARMONIZED_DIRNAME, current_timestamp, file_name.replace(" ", "_").lower(),
        )
    archive_paths["usage_tracking"] = USAGE_TRACKING_DIR_ARCHIVE.format(
        current_timestamp
    )
    archive_paths["user_client_map"] = USER_CLIENT_MAP_DIR_ARCHIVE.format(
        current_timestamp
    )
    archive_paths["file_detail"] = FILE_DETAIL_DIR_ARCHIVE.format(current_timestamp)
    archive_paths["client"] = CLIENT_DIR_ARCHIVE.format(current_timestamp)
    archive_paths["company_data"] = COMPANY_DATA_DIR_ARCHIVE.format(current_timestamp)
    archive_paths["data_distinct"] = DATA_DISTINCT_DIR_ARCHIVE.format(current_timestamp)
    archive_paths["cat_to_map"] = CATEGORY_TO_MODULE_MAP_DIR_ARCHIVE.format(
        current_timestamp
    )
    archive_paths["meta_table"] = META_TABLE_DIR_ARCHIVE.format(current_timestamp)
    archive_paths["meta_column_table"] = META_COLUMN_TABLE_DIR_ARCHIVE.format(
        current_timestamp
    )
    archive_paths["sme_cat_map"] = SME_CATEGORY_MAP_DIR_ARCHIVE.format(
        current_timestamp
    )
    archive_paths["category"] = CATEGORY_DIR_ARCHIVE.format(current_timestamp)
    archive_paths["data_distinct_file_map"] = DATA_DISTINCT_FILE_MAP_DIR_ARCHIVE.format(
        current_timestamp
    )

    archive_paths["users"] = USER_DIR_ARCHIVE.format(current_timestamp)
    archive_paths["notification"] = NOTIFICATION_DIR_ARCHIVE.format(current_timestamp)

    return archive_paths


def get_azure_seed_files_path(for_app_db=None):
    """Method for retriving all seed file path of Azure."""

    seed_file_path = []
    for _file in AZURE_SEED_FILE:
        seed_file_path.append("{0}/{1}/{2}.csv".format(AZURE_SEED_FOLDER, _file, _file))
    return seed_file_path


def get_action_cache_key(identifier, for_name=None):
    if for_name is not None:
        return ACTION_NAME_CACHE_KEY.format(identifier)
    return ACTION_ID_CACHE_KEY.format(identifier)


STORED_PROC_NAMES = {"report": "ingest_from_etl_multi"}


def get_sp_query_for_raw_data(pk_id, json_type):
    """Get query call stored procedure to snowflake"""
    return "CALL {0}('{1}', '{2}');".format(
        STORED_PROC_NAMES.get("report"), pk_id, json_type
    )


def get_sp_file_name(file_name):
    return f"SP_DATA_ROW_{file_name.upper().replace(' ','')}"


def get_dir_name_for_file(file_name):
    # return NORMALIZED_ADD_NEW_RECORD.format(file_name.lower().replace(" ", "_"))
    return NORMALIZED_AZURE_BASE_PATH.format(file_name.lower().replace(" ", "_"))
