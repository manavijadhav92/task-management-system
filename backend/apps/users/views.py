"""
Views for registration, login, logout, token refresh, and "current user".
"""

import datetime

import jwt
from django.contrib.auth.hashers import check_password, make_password
from pymongo.errors import DuplicateKeyError
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.common.jwt_utils import (
    create_access_token,
    create_refresh_token,
    decode_token,
    is_refresh_token_valid,
    revoke_refresh_token,
)
from apps.common.mongo import users_collection
from apps.common.responses import error_response, success_response

from .serializers import (
    LoginSerializer,
    RefreshSerializer,
    RegisterSerializer,
    UserPublicSerializer,
)


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Validation failed", serializer.errors, 400)

        data = serializer.validated_data
        doc = {
            "name": data["name"],
            "email": data["email"],
            "password": make_password(data["password"]),
            "created_at": datetime.datetime.now(datetime.timezone.utc),
        }

        try:
            result = users_collection().insert_one(doc)
        except DuplicateKeyError:
            return error_response(
                "Validation failed",
                {"email": ["A user with this email already exists."]},
                400,
            )

        doc["_id"] = result.inserted_id
        return success_response(
            "User registered successfully",
            UserPublicSerializer.from_doc(doc),
            201,
        )


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Validation failed", serializer.errors, 400)

        data = serializer.validated_data
        user = users_collection().find_one({"email": data["email"]})

        if not user or not check_password(data["password"], user["password"]):
            return error_response("Invalid email or password.", {}, 401)

        access = create_access_token(user["_id"])
        refresh = create_refresh_token(user["_id"])

        return success_response(
            "Login successful",
            {
                "access": access,
                "refresh": refresh,
                "user": UserPublicSerializer.from_doc(user),
            },
        )


class RefreshView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RefreshSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Validation failed", serializer.errors, 400)

        token = serializer.validated_data["refresh"]
        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            return error_response("Refresh token has expired.", {}, 401)
        except jwt.InvalidTokenError:
            return error_response("Invalid refresh token.", {}, 401)

        if payload.get("type") != "refresh":
            return error_response("Invalid token type.", {}, 401)

        if not is_refresh_token_valid(payload.get("jti")):
            return error_response("Refresh token has been revoked.", {}, 401)

        access = create_access_token(payload["user_id"])
        return success_response("Token refreshed", {"access": access})


class LogoutView(APIView):
    # Logout only needs a valid refresh token to revoke - it must not
    # require a still-valid access token, since a client should be able
    # to log out even after its short-lived access token has expired.
    permission_classes = [AllowAny]

    def post(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            return error_response(
                "Validation failed", {"refresh": ["This field is required."]}, 400
            )
        try:
            payload = decode_token(refresh)
            revoke_refresh_token(payload.get("jti"))
        except jwt.InvalidTokenError:
            pass  # Already invalid/expired - logout is idempotent either way.

        return success_response("Logged out successfully", None)


class MeView(APIView):
    def get(self, request):
        return success_response(
            "Success",
            {
                "id": request.user.id,
                "name": request.user.name,
                "email": request.user.email,
            },
        )
