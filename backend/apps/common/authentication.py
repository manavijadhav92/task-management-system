"""
Custom DRF authentication class: validates the JWT access token from the
`Authorization: Bearer <token>` header and loads the corresponding user
document from MongoDB, exposing it as request.user.
"""

import jwt
from bson import ObjectId
from bson.errors import InvalidId
from rest_framework import authentication, exceptions

from .jwt_utils import decode_token
from .mongo import users_collection


class MongoUser:
    """Thin wrapper so request.user behaves like an object, not a dict."""

    def __init__(self, doc):
        self._doc = doc
        self.id = str(doc["_id"])
        self.name = doc.get("name")
        self.email = doc.get("email")
        self.is_authenticated = True

    def __getitem__(self, key):
        return self._doc[key]


class JWTAuthentication(authentication.BaseAuthentication):
    keyword = "Bearer"

    def authenticate(self, request):
        header = authentication.get_authorization_header(request).decode("utf-8")
        if not header or not header.startswith(self.keyword + " "):
            return None

        token = header[len(self.keyword) + 1 :].strip()
        if not token:
            raise exceptions.AuthenticationFailed("No token provided.")

        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed("Access token has expired.")
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed("Invalid access token.")

        if payload.get("type") != "access":
            raise exceptions.AuthenticationFailed("Invalid token type.")

        try:
            user_doc = users_collection().find_one({"_id": ObjectId(payload["user_id"])})
        except InvalidId:
            raise exceptions.AuthenticationFailed("Invalid token subject.")

        if not user_doc:
            raise exceptions.AuthenticationFailed("User no longer exists.")

        return (MongoUser(user_doc), token)

    def authenticate_header(self, request):
        # Returning a value here tells DRF that a "credentials were absent
        # or invalid" failure should map to 401 Unauthorized (with a
        # WWW-Authenticate header), not 403 Forbidden.
        return self.keyword
