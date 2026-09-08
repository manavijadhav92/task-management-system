from django.http import JsonResponse
from django.urls import include, path


def health_check(request):
    return JsonResponse({"success": True, "message": "API is running"})


urlpatterns = [
    path("api/health/", health_check, name="health-check"),
    path("api/auth/", include("apps.users.urls")),
    path("api/tasks/", include("apps.tasks.urls")),
]
