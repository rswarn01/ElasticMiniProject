"""Controller for the user authentication related functions
"""
from elastic.constants import AUTHENTICATION_OR_AUTHORIZATION_FAILURE
import requests
import msal
import uuid
import logging
import base64

from flask import redirect, request, url_for
from flask import current_app as app

from elastic.extensions import guard, db
from elastic.models import User
from elastic.utils import Response
from ..models import user_schema


def increment_failed_attempt(user=None):
    if user is not None:
        User.update_user(
            user_id=user.user_id, failed_attempt=True,
        )

    return


def get_refresh_token_from_old_access_token():
    """Generate a new JWT token from the old token if it is expired

    Returns:
        [token]: JWT refresh token
    """
    token = guard.read_token_from_header()
    token_response = {"access_token": guard.refresh_jwt_token(token)}
    return token_response


def get_user_info():
    """Get user information from DB.

    Extract user id from jwt token to get user information.

    Returns:
        dict: user information
    """
    token = guard.read_token_from_header()
    user_id = guard.extract_jwt_token(token)["id"]
    user = User.identify(user_id)
    if user:
        return Response.success(user_schema.dump(user))
    return Response.failure(400, "Unable to identify the user")


def azure_get_token_from_post_data():
    """Uses the `code` returned from successfull authentication in azure active directory
    to get `access_token` for azure AD. Use this `access_token` to get user information
    from azure AD.

    Valid user is granted the `flask app's` JWT access_token.

    Returns:
        dict : JWT access token
    """
    # get data from form
    json_data = request.form.to_dict()
    code = json_data and json_data.get("code", None)
    redirect_uri = json_data and json_data.get("redirect_uri", None)

    # get from request body if form doesnt have code - should never happen
    if not code or not redirect_uri:
        json_data = request.get_json()
        code = json_data and json_data.get("code", None)
        redirect_uri = json_data and json_data.get("redirect_uri", None)
    if not code or not redirect_uri:
        return Response.failure(
            401,
            AUTHENTICATION_OR_AUTHORIZATION_FAILURE,
            payload="Missing Code or Redirect URI",
        )

    result = _build_msal_app().acquire_token_by_authorization_code(
        code, scopes=[app.config["SCOPE"]], redirect_uri=redirect_uri,  # frontend page
    )
    if "error" in result:
        logging.error("Error in response from microsoft graph api")
        return Response.failure(
            401, AUTHENTICATION_OR_AUTHORIZATION_FAILURE, payload=result
        )

    # get more info about the current user from the identity api using access_token
    json_data = requests.get(
        app.config["ENDPOINT"],
        headers={"Authorization": f"{result['token_type']} {result['access_token']}"},
    ).json()

    image = requests.get(
        app.config["IMAGE_ENDPOINT"],
        headers={"Authorization": f"{result['token_type']} {result['access_token']}"},
        stream=True,
    )
    logging.info("image from graph status: %d", image.status_code)

    image_bytes = None
    if image.status_code == 200:
        image_bytes = f"data:image/png;base64,{base64.b64encode(image.raw.read()).decode('utf-8')}"

    print("user info from graph: ", json_data, flush=True)
    logging.info(json_data)

    _email = json_data.get("mail", None) or json_data.get("userPrincipalName", None)
    if _email is None:
        logging.error("Email is not found in response")
        Response.failure(400, "No email id found for user")

    user = User.query.filter_by(email_address=_email).first()
    if not user:
        user = User.create_user(
            first_name=json_data.get("givenName"),
            last_name=json_data.get("surname"),
            email=_email,
            roles=User.ROLE_KEARNEY_USER,
            approved=True,
        )

    if user.is_active == 0:
        user.is_active = 1
        db.session.commit()

    response = {"access_token": guard.encode_jwt_token(user)}
    if image_bytes:
        response["image"] = image_bytes
    return response


def get_azure_login_url():
    """Get azure login url for the app"""
    auth_url = _build_auth_url(scopes=[app.config["SCOPE"]])
    return redirect(auth_url)


def get_azure_logout_url():
    """Get logout url and redirect to it."""
    return redirect(app.config["AUTHORITY"] + "/oauth2/v2.0/logout")


def _build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        app.config["AZURE_OAUTH_CLIENT_ID"],
        authority=authority or app.config["AUTHORITY"],
        client_credential=app.config["AZURE_OAUTH_CLIENT_SECRET"],
        token_cache=cache,
    )


def _build_auth_url(authority=None, scopes=None, state=None):
    return _build_msal_app(authority=authority).get_authorization_request_url(
        scopes or [],
        state=state or str(uuid.uuid4()),
        redirect_uri=url_for("api.get_token", _external=True),
    )
