"""
JWT creation/validation helpers, independent of Django's auth app (which
we don't use, since there is no relational User model).
"""

import uuid
from datetime import datetime, timezone

import jwt
from django.conf import settings

from .mongo import get_db


def _now():
    return datetime.now(timezone.utc)


def create_access_token(user_id):
    payload = {
        "user_id": str(user_id),
        "type": "access",
        "iat": _now(),
        "exp": _now() + settings.JWT_ACCESS_TOKEN_LIFETIME,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id):
    jti = str(uuid.uuid4())
    payload = {
        "user_id": str(user_id),
        "type": "refresh",
        "jti": jti,
        "iat": _now(),
        "exp": _now() + settings.JWT_REFRESH_TOKEN_LIFETIME,
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    # Store the refresh token's jti so it can be individually revoked on logout,
    # and so we can check "is this refresh token still valid" on refresh/logout.
    get_db()["refresh_tokens"].insert_one(
        {
            "jti": jti,
            "user_id": str(user_id),
            "expires_at": payload["exp"],
            "revoked": False,
        }
    )
    return token


def decode_token(token):
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


def revoke_refresh_token(jti):
    get_db()["refresh_tokens"].update_one({"jti": jti}, {"$set": {"revoked": True}})


def is_refresh_token_valid(jti):
    doc = get_db()["refresh_tokens"].find_one({"jti": jti})
    return bool(doc) and not doc.get("revoked", False)
