import time
import psutil
from django.utils import timezone
from task_manager.models import TaskInstance, SystemResources

INTERVAL = 5
_monitor_started = False


def start_monitor():
    global _monitor_started
    if _monitor_started:
        return

    _monitor_started = True

    import threading

    thread = threading.Thread(target=monitor_running_tasks, daemon=True)
    thread.start()


def monitor_running_tasks():
    while True:
        running_tasks = TaskInstance.objects.filter(state="RUNNING")
        now = timezone.now()

        for task in running_tasks:
            if not task.pid or not psutil.pid_exists(task.pid):
                # PID neexistuje → nestandardní ukončení
                task.state = "FAILED"
                task.end_time = now
                task.save(update_fields=["state", "end_time"])
                continue

            # PID existuje → zaznamenej CPU/memory
            try:
                process = psutil.Process(task.pid)
                cpu = process.cpu_percent(interval=0.1)
                memory = process.memory_info().rss // (1024 * 1024)
                elapsed = (now - task.start_time).total_seconds()

                SystemResources.objects.create(
                    cpu=round(cpu, 1),
                    memory=int(memory),
                    elapsed_seconds=elapsed,
                    task_instance=task,
                )
            except psutil.NoSuchProcess:
                task.state = "FAILED"
                task.end_time = now
                task.save(update_fields=["state", "end_time"])

        time.sleep(INTERVAL)
