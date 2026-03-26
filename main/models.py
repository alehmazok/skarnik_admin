from tinymce.models import HTMLField
from django.db import models


class Word(models.Model):
    external_id = models.IntegerField()
    letter = models.CharField(max_length=1)
    direction = models.CharField(max_length=31)
    text = models.CharField(max_length=127, db_index=True)
    translation = HTMLField()
    redirect_to = models.URLField(null=True, blank=True)
    stress = models.CharField(max_length=127, null=True, blank=True, help_text="Націск")

    class Meta:
        unique_together = ["external_id", "direction"]
        verbose_name = "Слова"
        verbose_name_plural = "Словы"

    def __str__(self):
        return f"({self.pk}) {self.text}"

    def to_typesense(self):
        return {
            "id": str(self.pk),
            "external_id": self.external_id,
            "letter": self.letter,
            "direction": self.direction,
            "text": self.text,
            "translation": self.translation,
        }

    @property
    def relative_link(self):
        return f"/{self.direction}/{self.id}"

    @property
    def relative_external_link(self):
        return f"/{self.direction}/{self.external_id}"


class Translation(models.Model):
    external_id = models.IntegerField()
    letter = models.CharField(max_length=1)
    direction = models.CharField(max_length=31)
    text = models.CharField(max_length=127)
    translation = HTMLField()

    class Meta:
        managed = False
        db_table = "translations"

    def to_word(self) -> Word:
        return Word(
            external_id=self.external_id,
            letter=self.letter,
            direction=self.direction,
            text=self.text,
            translation=self.translation,
        )
