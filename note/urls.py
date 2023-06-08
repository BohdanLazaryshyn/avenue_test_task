from django.urls import path, include
from rest_framework import routers

from note.views import NoteViewSet

app_name = "note_app"

routr = routers.DefaultRouter()
routr.register("notes", NoteViewSet)

urlpatterns = [
    path("", include(routr.urls)),
    path("create/", NoteViewSet.as_view({"put": "create"}), name="create_note"),
]
