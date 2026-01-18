from django.db import models

# Create your models here.


class Task(models.Model):
    number = models.PositiveSmallIntegerField()


class Configuration(models.Model):
    program = models.CharField(max_length=50)
    file_name = models.CharField(max_length=50)
    working_directory = models.CharField(max_length=200)
    additional_parameters = models.CharField(max_length=100, blank=True)


class System_resources(models.Model):
    cpu = models.PositiveSmallIntegerField()
    memory = models.PositiveSmallIntegerField()
    is_running = models.BooleanField()


class Schedule(models.Model):
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField()
