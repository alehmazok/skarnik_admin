from rest_framework import generics
from rest_framework.exceptions import NotFound

from .models import Word
from .serializers import WordSerializer


class WordByIdRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Word.objects.all()
    serializer_class = WordSerializer


class WordByExternalIdRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = WordSerializer

    def get_object(self):
        queryset = self.get_queryset()
        direction = self.kwargs.get('direction')
        external_id = self.kwargs.get('external_id')

        # Filter the queryset by direction and external_id
        obj = queryset.filter(direction=direction, external_id=external_id).first()

        if obj is None:
            raise NotFound("Word not found with the specified direction and external_id")

        return obj

    def get_queryset(self):
        return Word.objects.all()
