from django.http.response import Http404
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Word
from .serializers import WordSerializer


@api_view(['GET'])
def get_word_by_id(req, word_id):
    try:
        word = Word.objects.get(id=word_id)
        serializer = WordSerializer(word)
        return Response(serializer.data)
    except Word.DoesNotExist as e:
        raise Http404()


@api_view(['GET'])
def get_word_by_external_id(req, direction: str, external_id: int):
    try:
        word = Word.objects.get(direction=direction, external_id=external_id)
        serializer = WordSerializer(word)
        return Response(serializer.data)
    except Word.DoesNotExist as e:
        raise Http404()
