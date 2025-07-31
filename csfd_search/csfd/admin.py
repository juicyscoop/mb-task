from django.contrib import admin

from .models import Movie, Actor

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "url")
    search_fields = ("title",)

@admin.register(Actor)
class ActorAdmin(admin.ModelAdmin):
    list_display = ("name", "url")
    search_fields = ("name",)
