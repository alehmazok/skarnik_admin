from ckeditor.fields import RichTextField
from django.db import models


class Word(models.Model):
    external_id = models.IntegerField()
    letter = models.CharField(max_length=1)
    direction = models.CharField(max_length=31)
    text = models.CharField(max_length=127)
    translation = RichTextField()

    class Meta:
        unique_together = ['external_id', 'direction']

    def __str__(self):
        return f'({self.pk}) {self.text}'
