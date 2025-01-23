from rest_framework import serializers

from .models import Word


class WordSerializer(serializers.ModelSerializer):
    text = serializers.SerializerMethodField()

    class Meta:
        model = Word
        fields = '__all__'

    @staticmethod
    def get_text(obj: Word):
        if obj.stress and obj.stress != obj.text:
            return obj.stress
        return obj.text
