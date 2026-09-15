"""
Serializers for the tasks app. Plain Serializer (not ModelSerializer) since
tasks live in MongoDB, not a Django model.
"""
from datetime import date
from rest_framework import serializers

STATUS_CHOICES = ["TODO", "IN_PROGRESS", "COMPLETED"]
PRIORITY_CHOICES = ["LOW", "MEDIUM", "HIGH"]


class TaskWriteSerializer(serializers.Serializer):
    ##TDD test for the title muct be minimum 3 char 
    title = serializers.CharField(max_length=200, min_length=3, allow_blank=False)
    description = serializers.CharField(allow_blank=True, required=False, default="", max_length=1000)
    status = serializers.ChoiceField(choices=STATUS_CHOICES, default="TODO")
    priority = serializers.ChoiceField(choices=PRIORITY_CHOICES, default="MEDIUM")
    due_date = serializers.DateField(required=False, allow_null=True)
    assigned_to = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    def validate_title(self, value):
        if not value.strip():
            raise serializers.ValidationError("Title cannot be blank.")
        return value.strip()

    def validate_due_date(self, value):
        if value < date.today():
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value

class TaskUpdateSerializer(TaskWriteSerializer):
    """Same field rules as create, but every field is optional (for PATCH)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False


class TaskStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=STATUS_CHOICES)


class TaskReadSerializer(serializers.Serializer):
    @staticmethod
    def from_doc(doc):
        return {
            "id": str(doc["_id"]),
            "title": doc.get("title"),
            "description": doc.get("description", ""),
            "status": doc.get("status"),
            "priority": doc.get("priority"),
            "due_date": doc.get("due_date"),
            "created_by": doc.get("created_by"),
            "assigned_to": doc.get("assigned_to"),
            "created_at": doc.get("created_at"),
            "updated_at": doc.get("updated_at"),
        }
