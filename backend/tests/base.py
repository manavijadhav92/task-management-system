"""
Shared test base class.

Real integration tests would run against a real MongoDB instance (set via
MONGO_URI in .env). Since a real Mongo server may not always be available
(e.g. this sandbox, or a bare CI runner before `docker-compose up`), these
tests swap the MongoDB client for mongomock - an in-memory, API-compatible
fake - so the full request/response/DB-query cycle is still exercised.
"""

import mongomock
from rest_framework.test import APITestCase

from apps.common import mongo as mongo_module


class MongoBackedAPITestCase(APITestCase):
    def setUp(self):
        super().setUp()
        mongo_module._client = mongomock.MongoClient()
        mongo_module.create_indexes()

    def tearDown(self):
        mongo_module._client = None
        super().tearDown()
