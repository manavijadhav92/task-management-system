"""
Centralized MongoDB connection.

A single MongoClient is created per process and reused everywhere via
get_db(). This avoids opening a new connection on every request, which
would be wasteful and slow.
"""

from django.conf import settings
from pymongo import MongoClient

_client = None


def get_client():
    global _client
    if _client is None:
        _client = MongoClient(settings.MONGO_URI)
    return _client


def get_db():
    return get_client()[settings.MONGO_DB_NAME]


def users_collection():
    return get_db()["users"]


def tasks_collection():
    return get_db()["tasks"]


def create_indexes():
    """
    Create MongoDB indexes.

    Called once at startup (see apps/common/apps.py via AppConfig.ready,
    wired through the users app). Index choices, and why:

    - users.email (unique): every login/registration lookup is by email,
      and emails must be unique. A unique index enforces this at the
      database level (not just in application code) and makes the lookup
      O(log n) instead of a full collection scan.

    - tasks.created_by: the task list is always scoped to "tasks visible
      to this user" (created by or assigned to them), so this field is
      filtered on almost every request.

    - tasks.assigned_to: same reasoning as created_by - used to find
      "tasks assigned to me".

    - tasks.status and tasks.priority: used by the status/priority filter
      dropdowns in the UI on nearly every task-list request.

    - Compound index (created_by, status, priority): the task list
      endpoint commonly filters by owner AND status/priority together;
      a compound index lets MongoDB satisfy that combined filter with a
      single index instead of intersecting three separate index scans.

    We deliberately do NOT index fields like `description` (free text,
    rarely filtered on exactly) or `updated_at` (not used as a filter),
    since unused indexes only add write overhead and storage cost.
    """
    db = get_db()
    db["users"].create_index("email", unique=True)
    db["tasks"].create_index("created_by")
    db["tasks"].create_index("assigned_to")
    db["tasks"].create_index("status")
    db["tasks"].create_index("priority")
    db["tasks"].create_index([("created_by", 1), ("status", 1), ("priority", 1)])
    # jti: fast lookup/revocation of a specific refresh token on logout/refresh.
    db["refresh_tokens"].create_index("jti", unique=True)
    # TTL index: MongoDB automatically deletes expired refresh token records,
    # so revoked/expired tokens don't accumulate forever.
    db["refresh_tokens"].create_index("expires_at", expireAfterSeconds=0)
