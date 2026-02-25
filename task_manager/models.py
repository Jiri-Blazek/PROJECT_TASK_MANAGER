from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
import os

User = get_user_model()


class TaskInstance(models.Model):

    STATE_CHOICES = [
        ("RUNNING", "Running"),
        ("KILLED", "Killed"),
        ("FINISHED", "Finished"),
        ("FAILED", "Failed"),
        ("WAITING", "Waiting"),
    ]

    pid = models.PositiveIntegerField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    program = models.ForeignKey("Program", on_delete=models.CASCADE)
    file_name = models.CharField(max_length=50)
    working_directory = models.CharField(
        max_length=500,
        default=os.path.expanduser(
            r"C:\Users\blaze\OneDrive\Plocha\Programovani"
        ),  # např. domovský adresář
    )
    additional_parameters = models.CharField(max_length=100, blank=True)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField()
    state = models.CharField(
        max_length=20,
        choices=STATE_CHOICES,
        default="RUNNING",
    )

    def __str__(self):
        return f"Task {self.pid} – {self.user}"


class Program(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return f"{self.name}"


class SystemResources(models.Model):
    cpu = models.PositiveSmallIntegerField()
    memory = models.PositiveSmallIntegerField()
    task_instance = models.ForeignKey("TaskInstance", on_delete=models.CASCADE)
    elapsed_seconds = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Resources for Task {self.task_instance.pid}"
