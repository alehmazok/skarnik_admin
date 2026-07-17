from rest_framework import serializers

from .models import StressWord, Word


class WordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Word
        fields = '__all__'


class StressWordListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StressWord
        fields = ["id", "word", "lemma", "table_name"]


class StressWordDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = StressWord
        fields = ["id", "rows"]
