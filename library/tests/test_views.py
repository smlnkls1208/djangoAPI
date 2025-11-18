from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from library.models import Author, Book
import tempfile
import os

class BookViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@mail.com',
            password='123'
        )
        self.regular_user = User.objects.create_user(
            username='user',
            password='123'
        )
        self.author = Author.objects.create(name="Лев Толстой")

        self.pdf_file = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        self.pdf_file.write(b'%PDF-1.4\n')
        self.pdf_file.close()

    def tearDown(self):
        if os.path.exists(self.pdf_file.name):
            os.unlink(self.pdf_file.name)

    def test_admin_can_create_book(self):
        self.client.force_authenticate(user=self.admin_user)
        with open(self.pdf_file.name, 'rb') as f:
            response = self.client.post('/api/books/', {
                'title': 'Анна Каренина',
                'author': self.author.id,
                'year': 1877,
                'genre': 'роман',
                'category': 'художественная литература',
                'publisher': 'Русский вестник',
                'book_file': f,
                'book_type': 'fiction'
            })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 1)

    def test_regular_user_cannot_create_book(self):
        self.client.force_authenticate(user=self.regular_user)
        with open(self.pdf_file.name, 'rb') as f:
            response = self.client.post('/api/books/', {
                'title': 'Тест',
                'author': self.author.id,
                'year': 2025,
                'book_file': f,
                'book_type': 'fiction'
            })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anyone_can_read_books(self):
        Book.objects.create(
            title="Война и мир",
            author=self.author,
            year=1869,
            genre="роман",
            category="художественная литература",
            publisher="Русский вестник",
            book_file="fake.pdf",
            book_type='fiction'
        )
        response = self.client.get('/api/books/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_search_books(self):
        Book.objects.create(
            title="Мастер и Маргарита",
            author=self.author,
            year=1967,
            genre="фантастика",
            category="роман",
            publisher="Москва",
            book_file="fake.pdf",
            book_type='fiction'
        )
        response = self.client.get('/api/books/?search=Мастер')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertIn('Мастер', response.data[0]['title'])