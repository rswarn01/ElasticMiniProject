# import pandas as pd
from typing import Union
import logging, math
from werkzeug.exceptions import (
    Conflict,
    NotFound,
    BadRequest,
    Unauthorized,
    Forbidden,
    InternalServerError,
)

# from ipaddress import ip_address
# from werkzeug.utils import secure_filename
from flask_restx import abort

# from email_validator import validate_email

DESCENDING_VALUES = ["desc", "DESC", -1, "des", "DES", "D", "d"]


class Response:
    """Generic Response class to envelope the API response."""

    @staticmethod
    def success(
        data: Union[dict, list, str] = None, msg=None, pagination: dict = None,
    ) -> dict:
        """Construct a Enveloped Success response in JSON format.

        Args:
            data (Union[dict, list, str], optional): actual data to send.\
                If None, adds `{}` to response. Defaults to None.

        Returns:
            dict: Complete Enveloped success response object.

        ```py
            {
                "data": {},
                "success": true
            }
        ```
        """
        _resp = {"data": data if data is not None else {}, "success": True}

        # conditionally add msg
        if msg is not None:
            _resp["message"] = msg
        else:
            if isinstance(data, str):
                _resp["message"] = data

        # conditionally add pagination
        if pagination is not None:
            _resp["pagination"] = pagination
        return _resp

    @staticmethod
    def failure(error_code=500, msg=None, payload=None):
        """Construct a Enveloped Failure response in JSON format

        Args:
            error_code (int, optional): Http error codes. Defaults to 500.
            msg (str, optional): Desciption of the error. Defaults to None.
            payload (Union[dict, list, str], optional): Ant extra payload with the error message. Defaults to None.

        Returns:
            dict : Enveloped Failure response in JSON

        ```py
            {
                "error": {
                    "message" : "Error"
                    "payload" : {}
                },
                "success": False
            }
        ```
        """
        if msg is None:
            msg = Response.get_default_message(error_code)
        data = {"message": msg, "payload": payload}
        return abort(error_code, None, error=data, success=False)

    @staticmethod
    def get_default_message(error_code):
        """Get the default error message if not provided.

        Args:
            error_code (int): Http error code.

        Returns:
            str: Default error message or "Error"
        """
        error_msg = {
            "400": BadRequest.description,
            "404": NotFound.description,
            "401": Unauthorized.description,
            "500": InternalServerError.description,
            "403": Forbidden.description,
            "409": Conflict.description,
        }
        return error_msg.get(str(error_code)) or "Error"


def check_for_string(data):
    if not isinstance(data, str):
        raise ValueError("Must be string")
    return data


def get_pagination(args: dict, metadata: dict = None):
    """Creates pagination object to be sent to frontend.

    Args:
        args (dict): args accepted by routes. Must container `page_number` and `page_size`
        metadata (dict, optional): metadata as provided by the DAO layer. Must contain `total_items`

    Returns:
        dict: constructed pagination object
    """
    if not metadata:
        metadata = {}
    try:
        metadata["page_number"] = args["page_number"]
        metadata["page_size"] = args["page_size"]
        metadata["total_pages"] = (
            math.ceil(metadata["total_items"] / metadata["page_size"])
            if isinstance(metadata["page_size"], int)
            else None
        )

    except Exception as exc:
        logging.warning("Error while creating pagination object. Error: %s", str(exc))

    return metadata


class UserAlreadyExists(Exception):
    def __str__(self):
        return "User already exists"


class UserNotAllowed(Exception):
    def __str__(self) -> str:
        return "Exception Occured, User not allowed for this operation!"


class UserReactivated(Exception):
    def __str__(self):
        return "User account reactivated, Please edit the user details"


class UserDoesNotExist(Exception):
    def __str__(self):
        return "User does not exist"


class RecordNotFound(Exception):
    def __str__(self):
        return "Record Not Found"


class ClientUserAlreadyLinked(Exception):
    def __str__(self):
        self.msg = "Client user already linked"


class NormalizedFileAlreadyExists(Exception):
    def __init__(self):
        self.msg = "Please deactivate the existing file to move forward"
