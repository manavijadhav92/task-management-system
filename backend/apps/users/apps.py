from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"

    def ready(self):
        # Ensure MongoDB indexes exist as soon as the app starts.
        # Imported here (not at module load time) to avoid running this
        # during commands like `makemigrations` that don't need a DB.
        import os

        if os.environ.get("RUN_MAIN") or os.environ.get("DJANGO_SKIP_INDEXES") != "1":
            try:
                from apps.common.mongo import create_indexes

                create_indexes()
            except Exception:
                # Don't crash app startup if Mongo isn't reachable yet
                # (e.g. during static analysis or offline unit tests that
                # mock the collections). Connection errors surface clearly
                # on the first real request instead.
                pass
