from rest_framework import viewsets

from task.models import Task
from task.serializers import TaskListSerializer, TaskDetailSerializer, TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return TaskListSerializer
        if self.action == "retrieve":
            return TaskDetailSerializer
        return TaskSerializer
