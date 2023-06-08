from rest_framework import serializers

from task.models import Task


class TaskSerializer(serializers.ModelSerializer):
    completed = serializers.BooleanField(required=False)

    class Meta:
        model = Task
        fields = ("id", "title", "description", "due_date", "completed")


class TaskListSerializer(TaskSerializer):
    class Meta:
        model = Task
        fields = ("id", "title", "due_date", "completed")


class TaskDetailSerializer(TaskSerializer):
    class Meta:
        model = Task
        fields = ("id", "title", "description", "due_date", "completed")
