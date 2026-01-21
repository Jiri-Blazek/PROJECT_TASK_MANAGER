from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()


class TaskInstance(models.Model):
    pid = models.PositiveIntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Program(models.Model):
    program = models.CharField(max_length=50)
    task_instance = models.ForeignKey("TaskInstance", on_delete=models.CASCADE)


class Configuration(models.Model):
    file_name = models.CharField(max_length=50)
    working_directory = models.CharField(max_length=200)
    additional_parameters = models.CharField(max_length=100, blank=True)
    program = models.ForeignKey("Program", on_delete=models.CASCADE)


class SystemResources(models.Model):
    cpu = models.PositiveSmallIntegerField()
    memory = models.PositiveSmallIntegerField()
    date = models.DateTimeField()
    task_instance = models.ForeignKey("TaskInstance", on_delete=models.CASCADE)


class Schedule(models.Model):
    start_time = models.DateTimeField(default=timezone.now)
    # start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField()
    task_instance = models.ForeignKey("TaskInstance", on_delete=models.CASCADE)
