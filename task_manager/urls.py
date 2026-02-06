from django.urls import path
from task_manager import views


urlpatterns = [
    path("tasks/overview/", views.overview_view),  # overview_view
    # path("tasks/<slug:program_name>/", views.program_view),  # program_view
    path("tasks/word/", views.program_create_view),
]
