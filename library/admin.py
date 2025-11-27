from django.contrib import admin
from .models import Author, Book

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'year', 'publisher', 'book_type', 'genre']
    list_filter = ['book_type', 'genre', 'year']
    search_fields = ['title', 'author__name', 'publisher', 'genre']