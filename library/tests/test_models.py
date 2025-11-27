from django.test import TestCase
from django.core.exceptions import ValidationError
from library.models import Author, Book
from django.core.files.uploadedfile import SimpleUploadedFile


class AuthorModelTest(TestCase):
    def test_create_author(self):
        author = Author.objects.create(name="Михаил Булгаков", biography="Автор 'Мастера и Маргариты'")
        self.assertEqual(str(author), "Михаил Булгаков")
        self.assertEqual(author.name, "Михаил Булгаков")

    def test_unique_author_name(self):
        Author.objects.create(name="Фёдор Достоевский")
        with self.assertRaises(Exception):
            Author.objects.create(name="Фёдор Достоевский")


class BookModelTest(TestCase):
    def setUp(self):
        self.author = Author.objects.create(name="Лев Толстой")
        self.pdf = SimpleUploadedFile("test.pdf", b"%PDF-1.4\ncontent")

    def test_create_fiction_book(self):
        book = Book.objects.create(
            title="Анна Каренина",
            author=self.author,
            year=1877,
            genre="роман",
            category="художественная литература",
            publisher="Русский вестник",
            book_file=self.pdf,
            book_type='fiction'
        )
        self.assertEqual(str(book), "Анна Каренина (1877) — Лев Толстой")

    def test_unique_together_constraint(self):

        common = {
            'author': self.author,
            'year': 2020,
            'genre': 'роман',
            'category': 'художественная литература',
            'publisher': 'Эксмо',
            'book_file': self.pdf,
            'book_type': 'fiction'
        }
        Book.objects.create(title="Война и мир", **common)

        with self.assertRaises(Exception) as cm:
            Book.objects.create(title="Война и мир", **common)
        self.assertIn('unique', str(cm.exception).lower())

    def test_different_editions_allowed(self):

        base = {
            'title': "Мастер и Маргарита",
            'author': self.author,
            'genre': "фантастика",
            'category': "роман",
            'book_file': self.pdf,
            'book_type': 'fiction'
        }
        Book.objects.create(year=1967, publisher="Москва", **base)
        Book.objects.create(year=2020, publisher="Москва", **base)
        Book.objects.create(year=1967, publisher="Азбука", **base)

        self.assertEqual(Book.objects.filter(title="Мастер и Маргарита").count(), 3)