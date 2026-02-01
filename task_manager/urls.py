from django.urls import path
from django.http import HttpResponse
from django.shortcuts import render


def overview(request):
    print(request.GET)
    return render(request, "task_manager/overview.html")


def program(request, **kwargs):
    print(kwargs)
    return HttpResponse("test page" + request.path)


urlpatterns = [
    path("tasks/overview/", overview),
    path("tasks/<slug:program_name>/", program),
]
