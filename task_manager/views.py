from django.shortcuts import render, HttpResponse, redirect

from task_manager.models import TaskInstance
from django.contrib.auth.decorators import login_required
from task_manager.forms import TaskForm
from django.utils.text import slugify


@login_required
def overview_view(request):
    print(request.GET)
    if request.user.groups.filter(name="Computation").exists():
        tasks = TaskInstance.objects.all()
        return render(request, "task_manager/overview.html", {"tasksList": tasks})
    # else:
    #   return HttpResponse(request, "You dont have permission.")


def program_create_view(request):
    if request.method == "GET":
        form = TaskForm()
    else:
        form = TaskForm(request.POST)

        if form.is_valid():

            instance = form.save(commit=False)
            instance.pid = request.pid
            instance.slu = slugify(instance.name)
            print(instance)
            return redirect("/tasks/overview")

        print(form.cleaned_data)

    form = TaskForm()
    return render(request, "task_manager/word_form.html", {"form": form})
