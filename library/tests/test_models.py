from django.test import TestCase
from django.core.exceptions import ValidationError
from library.models import Author, Book


class AuthorModelTest(TestCase):
    def test_create_author(self):
        author = Author.objects.create(name="Михаил Булгаков", biography="его жена Олимпиада")
        self.assertEqual(str(author), "Михаил Булгаков")
        self.assertEqual(author.name, "Михаил Булгаков")

    def test_unique_author_name(self):
        Author.objects.create(name="Фёдор Достоевский")
        with self.assertRaises(Exception):
            Author.objects.create(name="Фёдор Достоевский")


class BookModelTest(TestCase):
    def setUp(self):
        self.author = Author.objects.create(name="Маргарет Митчелл")

    def test_create_fiction_book(self):
        book = Book.objects.create(
            title="Унесенные ветром",
            author=self.author,
            year=1936,
            genre="роман",
            category="историческая художественная литература",
            publisher="Macmillan Publishers",
            book_file="test.pdf",
            book_type='fiction'
        )
        self.assertEqual(str(book), "Унесенные ветром (1936) — Маргарет Митчелл")

    def test_unique_together_violation(self):
        common = {
            'author': self.author,
            'year': 1936,
            'genre': 'роман',
            'category': 'историческая художественная литература',
            'publisher': 'Macmillan Publishers',
            'book_file': 'test.pdf',
            'book_type': 'fiction'
        }
        Book.objects.create(title="Алгебра. 9 класс", **common)
        with self.assertRaises(Exception):
            Book.objects.create(title="Алгебра. 9 класс", **common)

    def test_textbook_same_edition_rejection(self):
        common = {
            'title': "Физика. 10 класс",
            'author': self.author,
            'genre': 'наука',
            'category': 'учебник',
            'publisher': 'Дрофа',
            'book_file': 'fake.pdf',
            'book_type': 'textbook'
        }
        Book.objects.create(year=2022, **common)

        with self.assertRaises(Exception) as cm:
            Book.objects.create(year=2022, **common)

        self.assertIsNotNone(cm.exception)

    def test_textbook_validation_error(self):
        common = {
            'title': "Физика. 10 класс",
            'author': self.author,
            'year': 2022,
            'genre': 'наука',
            'category': 'учебник',
            'publisher': 'Дрофа',
            'book_file': 'fake.pdf',
            'book_type': 'textbook'
        }

        Book.objects.create(**common)

        duplicate_book = Book(**common)

        with self.assertRaises(ValidationError) as cm:
            duplicate_book.full_clean()

        self.assertTrue(len(cm.exception.error_dict) > 0)