from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from task_manager.models import TaskInstance, Program, SystemResources
from django.contrib.auth.decorators import login_required
from task_manager.forms import TaskForm
from django.utils.text import slugify


from pathlib import Path

import os, signal
import subprocess
from openpyxl import Workbook
from docx import Document
from pptx import Presentation

# from django.http import JsonResponse
from django.views.decorators.http import require_POST
import psutil
from django.http import HttpResponseForbidden
import logging


def overview_view(request):
    programs = get_programs_for_tabs()
    if request.user.groups.filter(name="Computation").exists():
        tasks = TaskInstance.objects.all()
        return render(
            request,
            "task_manager/overview.html",
            {
                "tasksList": tasks,
                "program_name": "overview",
                "programs": programs,
            },
        )
    else:
        return HttpResponse("<h1>You dont have permission.</h1>")


def program_create_view(request, program_name):
    programs = get_programs_for_tabs()
    if program_name == "overview":
        program = None
    else:
        program = get_object_or_404(Program, slug=program_name)

    if request.method == "POST":
        form = TaskForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            if program:
                instance.program = program
            instance.user = request.user
            instance.save()
            instance.pid = run_task_instance(instance)
            instance.save()
            return redirect("/tasks/overview")
    else:
        form = TaskForm()

    return render(
        request,
        "task_manager/program_form.html",
        {
            "form": form,
            "program_name": program_name,
            "programs": programs,
        },
    )


def get_programs_for_tabs():
    programs = list(Program.objects.all().values("slug", "name"))
    programs.insert(0, {"slug": "overview", "name": "Overview"})
    return programs


########################### Run program ####################################


def run_task_instance(instance):
    slug = instance.program.slug
    file_name = instance.file_name
    working_dir = instance.working_directory
    additional_params = instance.additional_parameters or ""

    PROGRAM_PATHS = {
        "word": (r"C:\Program Files\Microsoft Office\Office16\WINWORD.EXE", ".docx"),
        "excel": (r"C:\Program Files\Microsoft Office\Office16\EXCEL.EXE", ".xlsx"),
        "powerpoint": (
            r"C:\Program Files\Microsoft Office\Office16\POWERPNT.EXE",
            ".pptx",
        ),
    }

    program_path, extension = PROGRAM_PATHS[slug]

    if not file_name.lower().endswith(extension):
        file_name += extension

    file_path = os.path.join(working_dir, file_name)

    if not os.path.exists(file_path):
        if slug == "excel":
            wb = Workbook()
            wb.save(file_path)

        elif slug == "word":
            doc = Document()
            doc.save(file_path)

        elif slug == "powerpoint":
            pres = Presentation()
            pres.save(file_path)

    cmd = (
        f"Start-Process -FilePath '{program_path}' "
        f"-ArgumentList '{file_path} {additional_params}' "
        f"-WorkingDirectory '{working_dir}' "
        f"-PassThru | Select-Object -ExpandProperty Id"
    )

    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", cmd],
            capture_output=True,
            text=True,
            check=True,
        )

        return int(result.stdout.strip())

    except Exception as e:
        print("Error during start of program:", e)
        return None


########################### Open working directory ####################################


def open_working_directory(request, task_id):
    task = get_object_or_404(TaskInstance, id=task_id)
    path = task.working_directory

    if os.path.exists(path):
        subprocess.Popen(["explorer", path], shell=True)

    return redirect("/tasks/overview/")


########################### Kill Job ##################################################
@require_POST
def kill_job_view(request, pid):
    task = get_object_or_404(TaskInstance, pid=pid)

    if task.user != request.user:
        return HttpResponseForbidden(
            "You dont have permission to kill this process.",
        )

    try:
        p = psutil.Process(pid)
        p.terminate()
        p.wait(timeout=3)

        task.state = "KILLED"
        task.save()

    except psutil.NoSuchProcess:
        # proces už neběží –  finished
        task.state = "FINISHED"
        task.save()

    except psutil.AccessDenied:
        task.state = "FAILED"
        task.save()
        return HttpResponseForbidden("Acces denied by OS.")

    return redirect("program_view", program_name="overview")
