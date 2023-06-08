from rest_framework import viewsets

from note.models import Note
from note.serializers import NoteSerializer, NoteListSerializer, NoteDetailSerializer


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return NoteListSerializer
        if self.action == "retrieve":
            return NoteDetailSerializer
        return NoteSerializer
