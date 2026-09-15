from datetime import date, timedelta

from bson import ObjectId
from rest_framework import status

from .base import MongoBackedAPITestCase


class TaskTestBase(MongoBackedAPITestCase):
    def setUp(self):
        super().setUp()
        self.client.post(
            "/api/auth/register/",
            {"name": "Owner", "email": "owner@example.com", "password": "Passw0rd1"},
        )
        login = self.client.post(
            "/api/auth/login/",
            {"email": "owner@example.com", "password": "Passw0rd1"},
        )
        self.token = login.data["data"]["access"]
        self.auth_header = {"HTTP_AUTHORIZATION": f"Bearer {self.token}"}

        self.client.post(
            "/api/auth/register/",
            {"name": "Other", "email": "other@example.com", "password": "Passw0rd1"},
        )
        other_login = self.client.post(
            "/api/auth/login/",
            {"email": "other@example.com", "password": "Passw0rd1"},
        )
        self.other_token = other_login.data["data"]["access"]
        self.other_auth_header = {"HTTP_AUTHORIZATION": f"Bearer {self.other_token}"}

    def create_task(self, **overrides):
        payload = {"title": "Write report", "description": "Q3 report", "priority": "HIGH"}
        payload.update(overrides)
        return self.client.post("/api/tasks/", payload, **self.auth_header)


class TaskCreateTests(TaskTestBase):
    def test_requires_authentication(self):
        resp = self.client.post("/api/tasks/", {"title": "No auth"})
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    ##TDD— Description maximum 1000 characters
    def test_create_task_description_max_1000_characters(self):
        description = "A" * 1001

        resp = self.create_task(description=description)

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
    ##TDD  — Due date cannot be in the past
    def test_create_task_past_due_date_rejected(self):
        yesterday = (date.today() - timedelta(days=1)).isoformat()

        resp = self.create_task(due_date=yesterday)

        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)


    def test_create_task_success(self):
        resp = self.create_task()
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data["data"]["title"], "Write report")
        self.assertEqual(resp.data["data"]["status"], "TODO")

    def test_create_task_blank_title_rejected(self):
        resp = self.create_task(title="   ")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_task_title_must_have_at_least_3_characters(self):
        resp = self.create_task(title="Hi")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_task_invalid_priority_rejected(self):
        resp = self.create_task(priority="URGENT")
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_due_date_is_stored_as_bson_encodable_datetime(self):
        """
        Regression test: DRF's DateField parses due_date into a plain
        datetime.date, but BSON (and therefore real MongoDB) has no
        encoder for date - only datetime. mongomock is more lenient than
        real MongoDB here, so this test encodes the stored value with
        bson.BSON.encode directly to catch what mongomock would let
        through silently.
        """
        import bson

        from apps.common.mongo import tasks_collection

        resp = self.create_task(due_date="2026-09-20")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        stored = tasks_collection().find_one({"_id": ObjectId(resp.data["data"]["id"])})
        bson.BSON.encode(stored)  # raises bson.errors.InvalidDocument if not encodable
        self.assertIsInstance(stored["due_date"], type(stored["created_at"]))


class TaskRetrieveUpdateDeleteTests(TaskTestBase):
    def setUp(self):
        super().setUp()
        self.task_id = self.create_task().data["data"]["id"]

    ## TDD for User cannot update another user's task
 
    def test_other_user_cannot_update_task(self):
        resp = self.client.patch(
        f"/api/tasks/{self.task_id}/",
        {"title": "Hacked task"},
        content_type="application/json",
        **self.other_auth_header,
    )
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    ## end the TDD for User cannot update another user's task
    def test_retrieve_task(self):
        resp = self.client.get(f"/api/tasks/{self.task_id}/", **self.auth_header)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["data"]["id"], self.task_id)

    def test_retrieve_invalid_id(self):
        resp = self.client.get("/api/tasks/not-a-valid-id/", **self.auth_header)
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_nonexistent_id(self):
        resp = self.client.get("/api/tasks/507f1f77bcf86cd799439011/", **self.auth_header)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_other_user_cannot_access(self):
        resp = self.client.get(f"/api/tasks/{self.task_id}/", **self.other_auth_header)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_task_put(self):
        resp = self.client.put(
            f"/api/tasks/{self.task_id}/",
            {"title": "Updated title", "priority": "LOW"},
            content_type="application/json",
            **self.auth_header,
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["data"]["title"], "Updated title")

    def test_partial_update_task_patch(self):
        resp = self.client.patch(
            f"/api/tasks/{self.task_id}/",
            {"priority": "LOW"},
            content_type="application/json",
            **self.auth_header,
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["data"]["priority"], "LOW")
        self.assertEqual(resp.data["data"]["title"], "Write report")

    def test_update_due_date_is_stored_as_bson_encodable_datetime(self):
        import bson

        resp = self.client.patch(
            f"/api/tasks/{self.task_id}/",
            {"due_date": "2026-12-25"},
            content_type="application/json",
            **self.auth_header,
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        from apps.common.mongo import tasks_collection

        stored = tasks_collection().find_one({"_id": ObjectId(self.task_id)})
        bson.BSON.encode(stored)

    def test_change_status(self):
        resp = self.client.patch(
            f"/api/tasks/{self.task_id}/status/",
            {"status": "IN_PROGRESS"},
            content_type="application/json",
            **self.auth_header,
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["data"]["status"], "IN_PROGRESS")

    def test_invalid_status_rejected(self):
        resp = self.client.patch(
            f"/api/tasks/{self.task_id}/status/",
            {"status": "DONE"},
            content_type="application/json",
            **self.auth_header,
        )
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_task(self):
        resp = self.client.delete(f"/api/tasks/{self.task_id}/", **self.auth_header)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        resp2 = self.client.get(f"/api/tasks/{self.task_id}/", **self.auth_header)
        self.assertEqual(resp2.status_code, status.HTTP_404_NOT_FOUND)

    def test_other_user_cannot_delete(self):
        resp = self.client.delete(f"/api/tasks/{self.task_id}/", **self.other_auth_header)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class TaskListFilterSearchSortPaginationTests(TaskTestBase):
    def setUp(self):
        super().setUp()
        self.create_task(title="Alpha task", description="General work", priority="HIGH", status="TODO")
        self.create_task(title="Beta task", description="General work", priority="LOW", status="IN_PROGRESS")
        self.create_task(title="Gamma report", description="General work", priority="MEDIUM", status="COMPLETED")

    def test_list_requires_auth(self):
        resp = self.client.get("/api/tasks/")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_returns_only_own_tasks(self):
        resp = self.client.get("/api/tasks/", **self.other_auth_header)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data["data"]["count"], 0)

    def test_list_all_own_tasks(self):
        resp = self.client.get("/api/tasks/", **self.auth_header)
        self.assertEqual(resp.data["data"]["count"], 3)

    def test_filter_by_status(self):
        resp = self.client.get("/api/tasks/?status=COMPLETED", **self.auth_header)
        self.assertEqual(resp.data["data"]["count"], 1)
        self.assertEqual(resp.data["data"]["results"][0]["title"], "Gamma report")

    def test_filter_by_priority(self):
        resp = self.client.get("/api/tasks/?priority=HIGH", **self.auth_header)
        self.assertEqual(resp.data["data"]["count"], 1)

    def test_search_by_title(self):
        resp = self.client.get("/api/tasks/?search=report", **self.auth_header)
        self.assertEqual(resp.data["data"]["count"], 1)
        self.assertEqual(resp.data["data"]["results"][0]["title"], "Gamma report")

    def test_sort_ascending_by_title(self):
        resp = self.client.get("/api/tasks/?ordering=title", **self.auth_header)
        titles = [t["title"] for t in resp.data["data"]["results"]]
        self.assertEqual(titles, sorted(titles))

    def test_pagination_page_size(self):
        resp = self.client.get("/api/tasks/?page_size=2", **self.auth_header)
        self.assertEqual(len(resp.data["data"]["results"]), 2)
        self.assertEqual(resp.data["data"]["count"], 3)
        self.assertIsNotNone(resp.data["data"]["next"])


class TaskStatsTests(TaskTestBase):
    def setUp(self):
        super().setUp()
        self.create_task(title="Task A", status="TODO", priority="HIGH")
        self.create_task(title="Task B", status="IN_PROGRESS", priority="LOW")
        self.create_task(title="Task C", status="COMPLETED", priority="HIGH")
        

    def test_stats_requires_auth(self):
        resp = self.client.get("/api/tasks/stats/")
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_stats_counts(self):
        resp = self.client.get("/api/tasks/stats/", **self.auth_header)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.data["data"]
        self.assertEqual(data["total"], 3)
        self.assertEqual(data["todo"], 1)
        self.assertEqual(data["in_progress"], 1)
        self.assertEqual(data["completed"], 1)
        self.assertEqual(data["high_priority_open"], 1)

    def test_stats_scoped_to_own_tasks(self):
        resp = self.client.get("/api/tasks/stats/", **self.other_auth_header)
        self.assertEqual(resp.data["data"]["total"], 0)
