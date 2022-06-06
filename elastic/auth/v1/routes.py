"""Routes for user authentication
Includes functions for login, register
"""
from flask_restx import Namespace, Resource

from . import controllers

api = Namespace("Auth", description="Auth related routes")
from elastic.extensions import guard
from elastic.models import User


@api.route("/refresh-token")
class RefreshToken(Resource):
    """class for refresh JWT token functions"""

    def get(self):
        """Get new JWT token from the old one only if it is expired

        Returns:
            [token]: JWT refresh token
        """
        return controllers.get_refresh_token_from_old_access_token()


@api.route("/identity")
class UserInfo(Resource):
    def get(self):
        """Get user information from token"""
        return controllers.get_user_info()


@api.route("/getAToken", endpoint="get_token")
class Authorized(Resource):
    # def get(self):
    #    "Get access token on azure authentication"
    #    return controllers.azure_get_token()

    def post(self):
        "Get access token on azure authentication"
        return controllers.azure_get_token_from_post_data()


@api.route("/login/azure")
class AzureLoginUrl(Resource):
    def get(self):
        """Get azure login url for the app"""
        return controllers.get_azure_login_url()


@api.route("/logout/azure")
class AuthLogoutUrl(Resource):
    def get(self):
        """Redirect to logout url"""
        return controllers.get_azure_logout_url()


@api.route("/login/simple_get_token")
class SimpleGetToken(Resource):
    def get(self):
        """Get azure login url for the app"""
        user = User.query.filter_by(user_id=1).first()
        response = {"access_token": guard.encode_jwt_token(user)}
        return response
