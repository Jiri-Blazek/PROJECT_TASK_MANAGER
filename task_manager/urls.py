from django.urls import path
from django.http import HttpResponse
from django.shortcuts import render


def task_manager(request):
    print(request.GET)
    return render(request, "task_manager/task_manager.html")


urlpatterns = [
    path("task_manager/", task_manager),
]
