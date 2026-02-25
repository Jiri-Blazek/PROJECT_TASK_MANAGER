from django.urls import path
from task_manager import views
from .views import tasks_status_api


urlpatterns = [
    path("tasks/overview/", views.overview_view),  # overview_view
    path(
        "tasks/<slug:program_name>/", views.program_create_view, name="program_view"
    ),  # program_view
    # path("tasks/word/", views.program_create_view),
    path(
        "tasks/open-dir/<int:task_id>/",
        views.open_working_directory,
        name="open_working_directory",
    ),
    path("tasks/kill/<int:pid>/", views.kill_job_view, name="kill_job"),
    path("tasks/history/<int:pid>/", views.job_history_view, name="job_history"),
    path("api/tasks-status/", tasks_status_api, name="tasks_status_api"),
]
