"""
Serializers for the users app.

These are plain rest_framework.serializers.Serializer subclasses (not
ModelSerializer), since there is no Django Model backing users - the data
lives in MongoDB and is accessed via PyMongo dicts.
"""

from rest_framework import serializers

from .validators import validate_password_strength


class RegisterSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150, allow_blank=False)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_password(self, value):
        error = validate_password_strength(value)
        if error:
            raise serializers.ValidationError(error)
        return value

    def validate_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Name is required.")
        return value.strip()

    def validate_email(self, value):
        return value.lower().strip()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        return value.lower().strip()


class RefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class UserPublicSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    email = serializers.EmailField()
    created_at = serializers.DateTimeField()

    @staticmethod
    def from_doc(doc):
        return {
            "id": str(doc["_id"]),
            "name": doc.get("name"),
            "email": doc.get("email"),
            "created_at": doc.get("created_at"),
        }
