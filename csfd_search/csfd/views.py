from django.shortcuts import render, get_object_or_404
from .models import Movie, Actor
from django.http import JsonResponse

from django.core.paginator import Paginator
from csfd.models import normalize


def search_view(request):
    query = request.GET.get("q", "")
    page_number = request.GET.get("page", 1)

    movies = Movie.objects.none()
    actors = Actor.objects.none()

    if query:
        normalized_query = normalize(query)
        movie_qs = Movie.objects.filter(title_normalized__icontains=normalized_query).order_by("title_normalized")
        actor_qs = Actor.objects.filter(name_normalized__icontains=normalized_query).order_by("name_normalized")

        movie_paginator = Paginator(movie_qs, 10)
        actor_paginator = Paginator(actor_qs, 10)

        movies = movie_paginator.get_page(page_number)
        actors = actor_paginator.get_page(page_number)

    return render(request, "csfd/search.html", {
        "query": query,
        "movies": movies,
        "actors": actors,
    })

def autocomplete_view(request):
    query = request.GET.get("q", "")
    results = []

    if query:
        normalized_query = normalize(query)

        movies = Movie.objects.filter(title_normalized__icontains=normalized_query)[:5]
        actors = Actor.objects.filter(name_normalized__icontains=normalized_query)[:5]

        results = [
            {"label": f"🎬 {movie.title}", "type": "movie", "id": movie.id}
            for movie in movies
        ] + [
            {"label": f"🎭 {actor.name}", "type": "actor", "id": actor.id}
            for actor in actors
        ]

    return JsonResponse(results, safe=False)

def movie_detail_view(request, pk):
    movie = get_object_or_404(Movie, pk=pk)
    actors = movie.actors.all()
    return render(request, "csfd/movie_detail.html", {"movie": movie, "actors": actors})

def actor_detail_view(request, pk):
    actor = get_object_or_404(Actor, pk=pk)
    movies = actor.movies.all()
    return render(request, "csfd/actor_detail.html", {"actor": actor, "movies": movies})
