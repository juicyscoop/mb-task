from django.db import models


from csfd.utils import normalize


class Movie(models.Model):
    url = models.URLField(unique=True)
    title = models.CharField(max_length=255, db_index=True)
    title_normalized = models.CharField(max_length=255, db_index=True)

    def save(self, *args, **kwargs):
        self.title_normalized = normalize(self.title)
        super().save(*args, **kwargs)

class Actor(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    name_normalized = models.CharField(max_length=255, db_index=True)
    url = models.URLField(unique=True)
    movies = models.ManyToManyField(Movie, related_name="actors")

    def save(self, *args, **kwargs):
        self.name_normalized = normalize(self.name)
        super().save(*args, **kwargs)
