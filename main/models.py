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
        verbose_name = 'Слова'
        verbose_name_plural = 'Словы'

    def __str__(self):
        return f'({self.pk}) {self.text}'


class Translation(models.Model):
    external_id = models.IntegerField()
    letter = models.CharField(max_length=1)
    direction = models.CharField(max_length=31)
    text = models.CharField(max_length=127)
    translation = RichTextField()

    class Meta:
        db_table = 'translations'

    def to_word(self) -> Word:
        return Word(
            external_id=self.external_id,
            letter=self.letter,
            direction=self.direction,
            text=self.text,
            translation=self.translation,
        )
