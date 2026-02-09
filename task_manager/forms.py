from django import forms
from django.utils import timezone
from task_manager.models import TaskInstance
from datetime import timedelta
import os


class TaskForm(forms.ModelForm):
    class Meta:
        model = TaskInstance
        fields = [
            "file_name",
            "working_directory",
            "additional_parameters",
            "start_time",
            "end_time",
        ]
        widgets = {
            "start_time": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "input",
                }
            ),
            "end_time": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                    "class": "input",
                }
            ),
            "file_name": forms.TextInput(attrs={"class": "input"}),
            "additional_parameters": forms.TextInput(attrs={"class": "input"}),
            "working_directory": forms.TextInput(attrs={"class": "input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Default start_time = now+1hour
        if not self.instance.pk:
            now = timezone.localtime()
            # datetime-local input
            fmt = "%Y-%m-%dT%H:%M"
            self.fields["start_time"].initial = now.strftime(fmt)
            self.fields["end_time"].initial = (now + timedelta(hours=1)).strftime(fmt)

        # Default working_directory
        if not self.fields["working_directory"].initial:
            self.fields["working_directory"].initial = os.path.expanduser("~")
