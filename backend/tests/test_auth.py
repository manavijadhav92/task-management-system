import jwt
from datetime import datetime, timedelta, timezone

from django.conf import settings
from rest_framework import status

from .base import MongoBackedAPITestCase

class RegistrationTests(MongoBackedAPITestCase):
    def test_register_success(self):
        resp = self.client.post(
            "/api/auth/register/",
            {"name": "Manavi", "email": "manavi@example.com", "password": "Passw0rd1"},
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertTrue(resp.data["success"])
        self.assertEqual(resp.data["data"]["email"], "manavi@example.com")
        self.assertNotIn("password", resp.data["data"])

    def test_duplicate_email_rejected(self):
        payload = {"name": "A", "email": "dup@example.com", "password": "Passw0rd1"}
        self.client.post("/api/auth/register/", payload)
        resp = self.client.post("/api/auth/register/", payload)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(resp.data["success"])

    def test_weak_password_rejected(self):
        resp = self.client.post(
            "/api/auth/register/",
            {"name": "A", "email": "weak@example.com", "password": "abc"},
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_email_rejected(self):
        resp = self.client.post(
            "/api/auth/register/",
            {"name": "A", "email": "not-an-email", "password": "Passw0rd1"},
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


class LoginTests(MongoBackedAPITestCase):
    def setUp(self):
        super().setUp()
        self.client.post(
            "/api/auth/register/",
            {"name": "Manavi", "email": "manavi@example.com", "password": "Passw0rd1"},
        )

    def test_login_success(self):
        resp = self.client.post(
            "/api/auth/login/",
            {"email": "manavi@example.com", "password": "Passw0rd1"},
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp.data["data"])
        self.assertIn("refresh", resp.data["data"])

    def test_login_wrong_password(self):
        resp = self.client.post(
            "/api/auth/login/",
            {"email": "manavi@example.com", "password": "WrongPass1"},
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_unknown_email(self):
        resp = self.client.post(
            "/api/auth/login/",
            {"email": "nouser@example.com", "password": "Passw0rd1"},
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)


class MeAndLogoutTests(MongoBackedAPITestCase):
    def setUp(self):
        super().setUp()
        self.client.post(
            "/api/auth/register/",
            {
                "name": "Manavi",
                "email": "manavi@example.com",
                "password": "Passw0rd1",
            },
        )

        login = self.client.post(
            "/api/auth/login/",
            {
                "email": "manavi@example.com",
                "password": "Passw0rd1",
            },
        )

        self.access = login.data["data"]["access"]
        self.refresh = login.data["data"]["refresh"]

    def test_me_with_expired_access_token(self):
        payload = jwt.decode(
            self.access,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_exp": False},
        )

        expired_token = jwt.encode(
            {
                "user_id": payload["user_id"],
                "type": "access",
                "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
            },
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM,
        )

        resp = self.client.get(
            "/api/auth/me/",
            HTTP_AUTHORIZATION=f"Bearer {expired_token}",
        )

        self.assertEqual(
            resp.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        ##end ###
     
    def test_me_requires_auth(self):
        resp = self.client.get("/api/auth/me/")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_with_valid_token(self):
        resp = self.client.get(
            "/api/auth/me/", HTTP_AUTHORIZATION=f"Bearer {self.access}"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["data"]["email"], "manavi@example.com")

    def test_me_with_invalid_token(self):
        resp = self.client.get(
            "/api/auth/me/", HTTP_AUTHORIZATION="Bearer not-a-real-token"
        )
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token_flow(self):
        resp = self.client.post("/api/auth/refresh/", {"refresh": self.refresh})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn("access", resp.data["data"])

    def test_logout_revokes_refresh_token(self):
        resp = self.client.post("/api/auth/logout/", {"refresh": self.refresh})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        resp2 = self.client.post("/api/auth/refresh/", {"refresh": self.refresh})
        self.assertEqual(resp2.status_code, status.HTTP_401_UNAUTHORIZED)
