"""
End-to-end flow test: register -> login -> receive JWT -> access a
protected endpoint -> create task -> view task -> update task -> change
status -> search/filter tasks -> delete task -> logout -> confirm the
access token is now unusable.

This exercises the full request -> URL routing -> view -> serializer ->
MongoDB round trip together, not each piece in isolation, which is the
point of an integration test as opposed to the unit tests in
test_auth.py / test_tasks.py.
"""

from rest_framework import status

from .base import MongoBackedAPITestCase


class FullUserFlowTests(MongoBackedAPITestCase):
    def test_full_task_management_flow(self):
        # 1. Register
        register_resp = self.client.post(
            "/api/auth/register/",
            {"name": "Manavi", "email": "manavi@example.com", "password": "Passw0rd1"},
        )
        self.assertEqual(register_resp.status_code, status.HTTP_201_CREATED)

        # 2. Login -> receive JWT
        login_resp = self.client.post(
            "/api/auth/login/",
            {"email": "manavi@example.com", "password": "Passw0rd1"},
        )
        self.assertEqual(login_resp.status_code, status.HTTP_200_OK)
        access = login_resp.data["data"]["access"]
        refresh = login_resp.data["data"]["refresh"]
        auth = {"HTTP_AUTHORIZATION": f"Bearer {access}"}

        # 3. Access a protected endpoint ("dashboard" data) with the token
        me_resp = self.client.get("/api/auth/me/", **auth)
        self.assertEqual(me_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(me_resp.data["data"]["email"], "manavi@example.com")

        stats_resp = self.client.get("/api/tasks/stats/", **auth)
        self.assertEqual(stats_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(stats_resp.data["data"]["total"], 0)

        # 4. Create task
        create_resp = self.client.post(
            "/api/tasks/",
            {"title": "Prepare project report", "description": "Q3 summary", "priority": "HIGH"},
            **auth,
        )
        self.assertEqual(create_resp.status_code, status.HTTP_201_CREATED)
        task_id = create_resp.data["data"]["id"]

        # 5. View task
        detail_resp = self.client.get(f"/api/tasks/{task_id}/", **auth)
        self.assertEqual(detail_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(detail_resp.data["data"]["title"], "Prepare project report")

        # 6. Update task
        update_resp = self.client.patch(
            f"/api/tasks/{task_id}/",
            {"description": "Q3 summary - final draft"},
            content_type="application/json",
            **auth,
        )
        self.assertEqual(update_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(update_resp.data["data"]["description"], "Q3 summary - final draft")

        # 7. Change status
        status_resp = self.client.patch(
            f"/api/tasks/{task_id}/status/",
            {"status": "IN_PROGRESS"},
            content_type="application/json",
            **auth,
        )
        self.assertEqual(status_resp.status_code, status.HTTP_200_OK)
        self.assertEqual(status_resp.data["data"]["status"], "IN_PROGRESS")

        # 8. Search/filter tasks
        search_resp = self.client.get("/api/tasks/?search=report", **auth)
        self.assertEqual(search_resp.data["data"]["count"], 1)

        filter_resp = self.client.get("/api/tasks/?status=IN_PROGRESS&priority=HIGH", **auth)
        self.assertEqual(filter_resp.data["data"]["count"], 1)

        no_match_resp = self.client.get("/api/tasks/?status=COMPLETED", **auth)
        self.assertEqual(no_match_resp.data["data"]["count"], 0)

        # Dashboard stats should now reflect the in-progress, high-priority task
        stats_resp_2 = self.client.get("/api/tasks/stats/", **auth)
        self.assertEqual(stats_resp_2.data["data"]["total"], 1)
        self.assertEqual(stats_resp_2.data["data"]["in_progress"], 1)
        self.assertEqual(stats_resp_2.data["data"]["high_priority_open"], 1)

        # 9. Delete task
        delete_resp = self.client.delete(f"/api/tasks/{task_id}/", **auth)
        self.assertEqual(delete_resp.status_code, status.HTTP_200_OK)

        gone_resp = self.client.get(f"/api/tasks/{task_id}/", **auth)
        self.assertEqual(gone_resp.status_code, status.HTTP_404_NOT_FOUND)

        # 10. Logout
        logout_resp = self.client.post("/api/auth/logout/", {"refresh": refresh})
        self.assertEqual(logout_resp.status_code, status.HTTP_200_OK)

        # The refresh token must now be unusable (can't silently get a new
        # access token after logout).
        refresh_after_logout = self.client.post("/api/auth/refresh/", {"refresh": refresh})
        self.assertEqual(refresh_after_logout.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_second_user_cannot_see_or_modify_first_users_tasks(self):
        self.client.post(
            "/api/auth/register/",
            {"name": "Alice", "email": "alice@example.com", "password": "Passw0rd1"},
        )
        alice_token = self.client.post(
            "/api/auth/login/", {"email": "alice@example.com", "password": "Passw0rd1"}
        ).data["data"]["access"]
        alice_auth = {"HTTP_AUTHORIZATION": f"Bearer {alice_token}"}

        self.client.post(
            "/api/auth/register/",
            {"name": "Bob", "email": "bob@example.com", "password": "Passw0rd1"},
        )
        bob_token = self.client.post(
            "/api/auth/login/", {"email": "bob@example.com", "password": "Passw0rd1"}
        ).data["data"]["access"]
        bob_auth = {"HTTP_AUTHORIZATION": f"Bearer {bob_token}"}

        task_id = self.client.post(
            "/api/tasks/", {"title": "Alice's private task"}, **alice_auth
        ).data["data"]["id"]

        # Bob's task list is empty - he can't see Alice's task.
        bob_list = self.client.get("/api/tasks/", **bob_auth)
        self.assertEqual(bob_list.data["data"]["count"], 0)

        # Bob can't read, update, or delete Alice's task directly by ID either.
        self.assertEqual(self.client.get(f"/api/tasks/{task_id}/", **bob_auth).status_code, 403)
        self.assertEqual(
            self.client.patch(
                f"/api/tasks/{task_id}/", {"title": "Hacked"}, content_type="application/json", **bob_auth
            ).status_code,
            403,
        )
        self.assertEqual(self.client.delete(f"/api/tasks/{task_id}/", **bob_auth).status_code, 403)
