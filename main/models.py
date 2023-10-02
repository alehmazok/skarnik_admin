from django.db import models


class Word(models.Model):
    text = models.CharField(max_length=127)
    translation = models.TextField()
