from django.apps import AppConfig
import os


class TaskManagerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "task_manager"

    def ready(self):
        if os.environ.get("RUN_MAIN") != "true":
            return

        from .monitor import start_monitor

        start_monitor()
