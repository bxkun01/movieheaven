from django.contrib import admin
from .models import Movie, Comment, MovieFolder,Like

admin.site.register(Movie)
admin.site.register(Comment)
admin.site.register(MovieFolder)
admin.site.register(Like)