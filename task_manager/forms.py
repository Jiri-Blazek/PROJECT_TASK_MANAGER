from django import forms
from task_manager.models import TaskInstance


class TaskForm(forms.ModelForm):
    class Meta:
        model = TaskInstance
        fields = [
            "program",
            "file_name",
            "working_directory",
            "additional_parameters",
            "start_time",
            "end_time",
        ]
