"""
Task CRUD, filtering, searching, sorting and pagination.

Authorization rule: a task is visible/editable by the user who created it
or the user it is assigned to. Nothing else has access to it.
"""

import datetime

from bson import ObjectId
from bson.errors import InvalidId
from rest_framework.views import APIView

from apps.common.mongo import tasks_collection
from apps.common.pagination import StandardResultsSetPagination
from apps.common.responses import error_response, success_response

from .serializers import (
    TaskReadSerializer,
    TaskStatusSerializer,
    TaskUpdateSerializer,
    TaskWriteSerializer,
)

ALLOWED_SORT_FIELDS = {"created_at", "updated_at", "due_date", "priority", "title", "status"}


def _visibility_filter(user_id):
    """Tasks the given user is allowed to see: created by or assigned to them."""
    return {"$or": [{"created_by": user_id}, {"assigned_to": user_id}]}


def _is_owner_or_assignee(task, user_id):
    return task.get("created_by") == user_id or task.get("assigned_to") == user_id


def _to_object_id(raw_id):
    try:
        return ObjectId(raw_id)
    except (InvalidId, TypeError):
        return None


def _normalize_due_date(value):
    """
    BSON (and therefore PyMongo) has no encoder for Python's plain
    datetime.date - only datetime.datetime. DRF's DateField gives us a
    `date`, so it must be converted to a midnight-UTC `datetime` before
    it's ever handed to PyMongo, or inserts/updates raise
    bson.errors.InvalidDocument.
    """
    if isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
        return datetime.datetime(
            value.year, value.month, value.day, tzinfo=datetime.timezone.utc
        )
    return value


class TaskListCreateView(APIView):
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        # Build the query as an explicit list of AND-ed clauses rather than
        # mixing top-level $or/$and keys, so the visibility filter, status
        # filter, priority filter, and search filter always combine
        # unambiguously regardless of which are present.
        clauses = [_visibility_filter(request.user.id)]

        status_param = request.query_params.get("status")
        if status_param:
            clauses.append({"status": status_param})

        priority_param = request.query_params.get("priority")
        if priority_param:
            clauses.append({"priority": priority_param})

        search = request.query_params.get("search")
        if search:
            clauses.append(
                {
                    "$or": [
                        {"title": {"$regex": search, "$options": "i"}},
                        {"description": {"$regex": search, "$options": "i"}},
                    ]
                }
            )

        query = {"$and": clauses}

        sort_field = request.query_params.get("ordering", "-created_at")
        direction = -1 if sort_field.startswith("-") else 1
        sort_field = sort_field.lstrip("-")
        if sort_field not in ALLOWED_SORT_FIELDS:
            sort_field = "created_at"
            direction = -1

        cursor = tasks_collection().find(query).sort(sort_field, direction)
        results = [TaskReadSerializer.from_doc(doc) for doc in cursor]

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(results, request, view=self)
        return paginator.get_paginated_response(page)

    def post(self, request):
        serializer = TaskWriteSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Validation failed", serializer.errors, 400)

        now = datetime.datetime.now(datetime.timezone.utc)
        data = serializer.validated_data
        doc = {
            "title": data["title"],
            "description": data.get("description", ""),
            "status": data.get("status", "TODO"),
            "priority": data.get("priority", "MEDIUM"),
            "due_date": _normalize_due_date(data.get("due_date")),
            "created_by": request.user.id,
            "assigned_to": data.get("assigned_to") or None,
            "created_at": now,
            "updated_at": now,
        }
        result = tasks_collection().insert_one(doc)
        doc["_id"] = result.inserted_id
        return success_response("Task created successfully", TaskReadSerializer.from_doc(doc), 201)


class TaskDetailView(APIView):
    def _get_task_or_error(self, task_id, user):
        oid = _to_object_id(task_id)
        if oid is None:
            return None, error_response("Invalid task ID.", {}, 400)

        task = tasks_collection().find_one({"_id": oid})
        if not task:
            return None, error_response("Task not found.", {}, 404)

        if not _is_owner_or_assignee(task, user.id):
            return None, error_response(
                "You do not have permission to access this task.", {}, 403
            )

        return task, None

    def get(self, request, task_id):
        task, err = self._get_task_or_error(task_id, request.user)
        if err:
            return err
        return success_response("Success", TaskReadSerializer.from_doc(task))

    def put(self, request, task_id):
        return self._update(request, task_id, partial=False)

    def patch(self, request, task_id):
        return self._update(request, task_id, partial=True)

    def _update(self, request, task_id, partial):
        task, err = self._get_task_or_error(task_id, request.user)
        if err:
            return err

        serializer_class = TaskUpdateSerializer if partial else TaskWriteSerializer
        serializer = serializer_class(data=request.data, partial=partial)
        if not serializer.is_valid():
            return error_response("Validation failed", serializer.errors, 400)

        update = {k: v for k, v in serializer.validated_data.items()}
        if "due_date" in update:
            update["due_date"] = _normalize_due_date(update["due_date"])
        update["updated_at"] = datetime.datetime.now(datetime.timezone.utc)

        tasks_collection().update_one({"_id": task["_id"]}, {"$set": update})
        updated = tasks_collection().find_one({"_id": task["_id"]})
        return success_response("Task updated successfully", TaskReadSerializer.from_doc(updated))

    def delete(self, request, task_id):
        task, err = self._get_task_or_error(task_id, request.user)
        if err:
            return err

        tasks_collection().delete_one({"_id": task["_id"]})
        return success_response("Task deleted successfully", None)


class TaskStatsView(APIView):
    def get(self, request):
        base = _visibility_filter(request.user.id)
        counts = {}
        for value in ("TODO", "IN_PROGRESS", "COMPLETED"):
            counts[value] = tasks_collection().count_documents({"$and": [base, {"status": value}]})
        high_priority = tasks_collection().count_documents(
            {"$and": [base, {"priority": "HIGH"}, {"status": {"$ne": "COMPLETED"}}]}
        )
        total = sum(counts.values())
        return success_response(
            "Success",
            {
                "total": total,
                "todo": counts["TODO"],
                "in_progress": counts["IN_PROGRESS"],
                "completed": counts["COMPLETED"],
                "high_priority_open": high_priority,
            },
        )


class TaskStatusView(APIView):
    def patch(self, request, task_id):
        oid = _to_object_id(task_id)
        if oid is None:
            return error_response("Invalid task ID.", {}, 400)

        task = tasks_collection().find_one({"_id": oid})
        if not task:
            return error_response("Task not found.", {}, 404)

        if not _is_owner_or_assignee(task, request.user.id):
            return error_response(
                "You do not have permission to access this task.", {}, 403
            )

        serializer = TaskStatusSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response("Validation failed", serializer.errors, 400)

        tasks_collection().update_one(
            {"_id": task["_id"]},
            {
                "$set": {
                    "status": serializer.validated_data["status"],
                    "updated_at": datetime.datetime.now(datetime.timezone.utc),
                }
            },
        )
        updated = tasks_collection().find_one({"_id": task["_id"]})
        return success_response("Task status updated successfully", TaskReadSerializer.from_doc(updated))
