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
def get_word_by_external_id(req):
    try:
        external_id = int(req.query_params.get('external_id', '0'))
        word = Word.objects.get(external_id=external_id)
        serializer = WordSerializer(word)
        return Response(serializer.data)
    except Word.DoesNotExist as e:
        raise Http404()
