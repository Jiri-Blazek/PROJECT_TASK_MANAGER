from task_manager.models import Program


def create_prog():
    for n in range(100, 200):
        Program.objects.create(
            program="word" + str(n),
        )
