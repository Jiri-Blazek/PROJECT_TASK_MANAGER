from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class TaskInstance(models.Model):
    pid = models.PositiveIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    program = models.ForeignKey("Program", on_delete=models.CASCADE)
    file_name = models.CharField(max_length=50)
    working_directory = models.CharField(max_length=200)
    additional_parameters = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Task {self.pid} – {self.user}"


class Program(models.Model):
    program = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.program}"


class SystemResources(models.Model):
    cpu = models.PositiveSmallIntegerField()
    memory = models.PositiveSmallIntegerField()
    date = models.DateTimeField()
    task_instance = models.ForeignKey("TaskInstance", on_delete=models.CASCADE)

    def __str__(self):
        return f"Resources for Task {self.task_instance.pid}"


class Schedule(models.Model):
    start_time = models.DateTimeField(default=timezone.now)
    # start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField()
    task_instance = models.ForeignKey("TaskInstance", on_delete=models.CASCADE)

    def __str__(self):
        return f"Schedule for Task {self.task_instance.pid}"
