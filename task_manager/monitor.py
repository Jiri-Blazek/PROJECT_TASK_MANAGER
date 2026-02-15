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
        # Kontrolujeme jen tasky, které mají stav RUNNING
        running_tasks = TaskInstance.objects.filter(state="RUNNING")

        for task in running_tasks:
            if not task.pid:
                continue

            # Pokud proces už neexistuje, necháme stav tak, jak byl nastaven (FINISHED / FAILED)
            if not psutil.pid_exists(task.pid):
                continue

            # Poslední zaznamenaná metrika
            last_entry = (
                SystemResources.objects.filter(task_instance=task)
                .order_by("-created_at")
                .first()
            )

            now = timezone.now()
            if last_entry:
                diff = (now - last_entry.created_at).total_seconds()
                if diff < INTERVAL:
                    continue  # zamezíme zbytečnému zapisování příliš často

            # Získání aktuálních dat procesu
            try:
                process = psutil.Process(task.pid)
                cpu = process.cpu_percent(interval=0.1)
                memory = process.memory_info().rss // (1024 * 1024)  # MB

                # Zapisujeme jen pro RUNNING tasky
                SystemResources.objects.create(
                    cpu=round(cpu, 1), memory=int(memory), task_instance=task
                )

            except psutil.NoSuchProcess:
                # Proces už mezitím skončil, necháme stav jak je
                continue

        time.sleep(INTERVAL)
