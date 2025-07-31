from django.core.management.base import BaseCommand
from csfd.models import Actor, Movie
from csfd.utils import normalize

class Command(BaseCommand):
    help = "Update normalized fields for existing data"

    def handle(self, *args, **kwargs):
        updated_actors = 0
        for actor in Actor.objects.all():
            normalized = normalize(actor.name)
            if actor.name_normalized != normalized:
                actor.name_normalized = normalized
                actor.save()
                updated_actors += 1

        updated_movies = 0
        for movie in Movie.objects.all():
            normalized = normalize(movie.title)
            if movie.title_normalized != normalized:
                movie.title_normalized = normalized
                movie.save()
                updated_movies += 1

        self.stdout.write(f"✅ Updated {updated_actors} actors and {updated_movies} movies.")
