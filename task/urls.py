from django.urls import path, include
from rest_framework import routers

from task.views import TaskViewSet

router = routers.DefaultRouter()
router.register("tasks", TaskViewSet)

urlpatterns = [
    path("", include(router.urls)),
]


app_name = "task_app"
