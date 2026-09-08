from django.urls import path

from .views import TaskDetailView, TaskListCreateView, TaskStatsView, TaskStatusView

urlpatterns = [
    path("", TaskListCreateView.as_view(), name="task-list-create"),
    path("stats/", TaskStatsView.as_view(), name="task-stats"),
    path("<str:task_id>/", TaskDetailView.as_view(), name="task-detail"),
    path("<str:task_id>/status/", TaskStatusView.as_view(), name="task-status"),
]
