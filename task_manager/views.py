from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from task_manager.models import TaskInstance, Program, SystemResources
from django.contrib.auth.decorators import login_required
from task_manager.forms import TaskForm
from django.utils.text import slugify
from django.db.models import OuterRef, Subquery
from collections import defaultdict
import json
from django.core.paginator import Paginator


import os
import subprocess
from openpyxl import Workbook
from docx import Document
from pptx import Presentation

from django.utils import timezone

import threading


from django.views.decorators.http import require_POST
import psutil
from django.http import HttpResponseForbidden


from django.utils import timezone

from django.http import JsonResponse

########################### Overview ####################################


# @login_required
def overview_view(request):
    # if not request.user.groups.filter(name="Computation").exists():
    #   return HttpResponse("<h1>You dont have permission.</h1>")

    programs = get_programs_for_tabs()
    now = timezone.now()

    latest_resources = SystemResources.objects.filter(
        task_instance=OuterRef("pk")
    ).order_by("-created_at")

    tasks = TaskInstance.objects.annotate(
        last_cpu=Subquery(latest_resources.values("cpu")[:1]),
        last_memory=Subquery(latest_resources.values("memory")[:1]),
        last_measure_time=Subquery(latest_resources.values("created_at")[:1]),
    ).select_related("user", "program")

    task_data = []

    for task in tasks:
        # CPU / Memory
        if task.state == "RUNNING":
            cpu = task.last_cpu or 0
            memory = task.last_memory or 0
        else:
            cpu = 0
            memory = 0

        # Running time
        if task.state == "RUNNING":
            running_time_sec = (now - task.start_time).total_seconds()
        elif task.end_time:
            running_time_sec = (task.end_time - task.start_time).total_seconds()
        else:
            running_time_sec = 0

        hours, remainder = divmod(int(running_time_sec), 3600)
        minutes, seconds = divmod(remainder, 60)
        running_time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        task_data.append(
            {
                "task": task,
                "cpu": cpu,
                "memory": memory,
                "running_time_sec": running_time_sec,
                "running_time_str": running_time_str,
            }
        )

        # ------------------ Preparation of inputs for charts ----------------
    program_totals = defaultdict(lambda: {"cpu": 0, "memory": 0})

    for entry in task_data:
        prog_name = entry["task"].program.name
        program_totals[prog_name]["cpu"] += entry["cpu"]
        program_totals[prog_name]["memory"] += entry["memory"]

    # Celkem
    total_cpu = sum(v["cpu"] for v in program_totals.values())
    total_memory = sum(v["memory"] for v in program_totals.values())

    # seznamy pro grafy
    cpu_labels = list(program_totals.keys()) + ["Total"]
    used_cpus = [v["cpu"] for v in program_totals.values()] + [total_cpu]
    memory_labels = list(program_totals.keys()) + ["Total"]
    used_memory = [v["memory"] for v in program_totals.values()] + [total_memory]

    # -------------------------------------------------------------------
    # task_list = TaskInstance.objects.all()
    # paginator = Paginator(task_list, per_page=5)
    # page_number = request.GET.get("page", 1)
    # page = paginator.get_page(page_number)
    # page_range = paginator.get_elided_page_range(page.number, on_each_side=2, on_ends=1)
    return render(
        request,
        "task_manager/overview.html",
        {
            #      "paginator": paginator,
            #     "page": page,
            # "page_range": page_range,
            "tasksData": task_data,
            "program_name": "overview",
            "programs": programs,
            "cpu_labels": cpu_labels,
            "used_cpus": used_cpus,
            "memory_labels": memory_labels,
            "used_memory": used_memory,
        },
    )


########################### Form for submiting ####################################


# @login_required
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
            instance.pid, instance.state = run_task_instance(instance)
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


########################### Tabs for programs ####################################


def get_programs_for_tabs():
    programs = list(Program.objects.all().values("slug", "name"))
    programs.insert(0, {"slug": "overview", "name": "Overview"})
    return programs


########################### Run program ####################################


# ------------------ Preparation of inputs for command line ----------------
def run_task_instance(instance):

    slug = instance.program.slug
    file_name = instance.file_name
    working_dir = instance.working_directory
    additional_params = instance.additional_parameters or ""
    start_time = instance.start_time
    end_time = instance.end_time

    PROGRAM_PATHS = {
        "word": (r"C:\Program Files\Microsoft Office\Office16\WINWORD.EXE", ".docx"),
        "excel": (r"C:\Program Files\Microsoft Office\Office16\EXCEL.EXE", ".xlsx"),
        "powerpoint": (
            r"C:\Program Files\Microsoft Office\Office16\POWERPNT.EXE",
            ".pptx",
        ),
    }

    program_path, extension = PROGRAM_PATHS[slug]

    # Add extension to file name
    file_name = file_name + extension

    file_path = os.path.join(working_dir, file_name)

    # Generation of file if not exists
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

    # actual time
    now = timezone.now()

    # ------------------ Function for start of task ----------------
    def start_program():
        try:
            cmd = (
                f"Start-Process -FilePath '{program_path}' "
                f"-ArgumentList '{file_path} {additional_params}' "
                f"-WorkingDirectory '{working_dir}' "
                f"-PassThru | Select-Object -ExpandProperty Id"
            )
            result = subprocess.run(
                ["powershell", "-NoProfile", "-Command", cmd],
                capture_output=True,
                text=True,
                check=True,
            )
            pid = int(result.stdout.strip())

            # set parameters of task
            instance.pid = pid
            instance.state = "RUNNING"
            instance.save()

            # stop the process based on end_time
            if end_time:
                delay = (end_time - timezone.now()).total_seconds()
                if delay > 0:
                    threading.Timer(
                        delay, terminate_process, args=(pid, instance)
                    ).start()

            return pid

        except Exception as e:
            print("Error during start of program:", e)
            instance.pid = None
            instance.state = "FAILED"
            instance.save()
            return None

    # ------------------ Function for termination of task ----------------
    def terminate_process(pid, instance):
        try:
            subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True)
            instance.state = "FINISHED"
            instance.save()
        except Exception as e:
            print("Error during termination:", e)
            instance.state = "FAILED"
            instance.save()

        # ------------------ Main function ----------------

    if start_time <= now:
        # Run immediatelly
        pid = start_program()
        return pid, instance.state
    else:
        # Delayed start
        instance.pid = None
        instance.state = "WAITING"
        instance.save()

        # Timne to start estimation
        delay = (start_time - now).total_seconds()
        threading.Timer(delay, start_program).start()

        return instance.pid, instance.state


########################### Open working directory ####################################


def open_working_directory(request, task_id):
    task = get_object_or_404(TaskInstance, id=task_id)
    path = task.working_directory

    if os.path.exists(path):
        subprocess.Popen(["explorer", path], shell=True)

    return redirect("/tasks/overview/")


########################### Get History ####################################


def job_history_view(request, pid):
    history = get_object_or_404(SystemResources, pid=pid)
    # history = get_task_history(task_id)  # např. seznam paměti a CPU

    return HttpResponseForbidden(
        request, "You dont have permission to kill this process."
    )


########################### Kill Job ##################################################
@require_POST
def kill_job_view(request, pid):
    task = get_object_or_404(TaskInstance, pid=pid)

    if task.user != request.user:
        return HttpResponseForbidden("You dont have permission to kill this process.")

    now = timezone.now()

    try:
        p = psutil.Process(pid)
        p.terminate()
        p.wait(timeout=3)
        task.state = "KILLED"
        task.end_time = now
        task.save()
    except psutil.NoSuchProcess:
        # proces už neběží → nestandardní ukončení
        task.state = "FAILED"
        task.end_time = now
        task.save()
    except psutil.AccessDenied:
        task.state = "FAILED"
        task.end_time = now
        task.save()
        return HttpResponseForbidden("Access denied by OS.")

    return redirect("program_view", program_name="overview")


########################### Task monitoring ##################################################


from django.http import JsonResponse
from django.utils import timezone
from .models import TaskInstance, SystemResources
import psutil


def tasks_status_api(request):
    tasks = TaskInstance.objects.all()
    tasks_list = []

    for task in tasks:
        # automaticky označit RUNNING task jako FAILED, pokud PID neexistuje
        if task.state == "RUNNING":
            if not task.pid or not psutil.pid_exists(task.pid):
                task.state = "FAILED"
                task.save()

        latest = (
            SystemResources.objects.filter(task_instance=task)
            .order_by("-created_at")
            .first()
        )

        if task.state == "RUNNING":
            running_time_sec = (timezone.now() - task.start_time).total_seconds()
            cpu = latest.cpu if latest else 0
            memory = latest.memory if latest else 0
        elif task.state == "WAITING":
            running_time_sec = 0
            cpu = memory = 0
        else:
            if latest:
                running_time_sec = (latest.created_at - task.start_time).total_seconds()
            else:
                running_time_sec = 0
            cpu = memory = 0

        tasks_list.append(
            {
                "pid": task.pid,
                "state": task.state,
                "cpu": cpu,
                "memory": memory,
                "start_time": task.start_time.isoformat(),
                "running_time_sec": int(running_time_sec),
            }
        )

    return JsonResponse({"tasks": tasks_list})
