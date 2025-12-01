from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from library.models import Author, Book
from django.core.files.uploadedfile import SimpleUploadedFile


class BookAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(
            username='admin', password='123'
        )
        self.user = User.objects.create_user(
            username='user', password='123'
        )
        self.author = Author.objects.create(name="Антуан де Сент-Экзюпери")

    def get_pdf(self, name="book.pdf"):
        return SimpleUploadedFile(
            name=name,
            content=b'%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\nxref\n0 3\n0000000000 65535 f\n0000000010 00000 n\n0000000053 00000 n\ntrailer<</Size 3/Root 1 0 R>>\nstartxref\n102\n%%EOF',
            content_type='application/pdf'
        )

    def test_admin_can_create_book(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/api/books/', {
            'title': 'Маленький принц',
            'author': self.author.id,
            'year': 1943,
            'genre': 'аллегория',
            'category': 'повесть',
            'publisher': 'Gallimard',
            'book_file': self.get_pdf("prince.pdf"),
            'book_type': 'fiction'
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 1)

    def test_regular_user_cannot_create_book(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/books/', {
            'title': 'Тест',
            'author': self.author.id,
            'year': 2025,
            'genre': 'тест',
            'category': 'тест',
            'publisher': 'Тест',
            'book_file': self.get_pdf("test.pdf"),
            'book_type': 'fiction'
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_anyone_can_read_books(self):
        Book.objects.create(
            title="Маленький принц",
            author=self.author,
            year=1943,
            genre="аллегория",
            category="повесть",
            publisher="Gallimard",
            book_file=self.get_pdf("prince2.pdf"),
            book_type='fiction'
        )
        response = self.client.get('/api/books/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_search_books(self):
        Book.objects.create(
            title="Преступление и наказание",
            author=self.author,
            year=1866,
            genre="психологический роман",
            category="роман",
            publisher="Русский вестник",
            book_file=self.get_pdf("crime.pdf"),
            book_type='fiction'
        )
        response = self.client.get('/api/books/?search=Преступление')
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data['results']), 0)
        self.assertIn('Преступление', response.data['results'][0]['title'])

    def test_invalid_year_rejected(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post('/api/books/', {
            'title': 'Тест',
            'author': self.author.id,
            'year': 999,
            'genre': 'роман',
            'category': 'тест',
            'publisher': 'Издатель',
            'book_file': self.get_pdf("bad_year.pdf"),
            'book_type': 'fiction'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn('Год должен быть', str(response.data))

    def test_duplicate_rejected_via_api(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            'title': 'Дубль',
            'author': self.author.id,
            'year': 2020,
            'genre': 'тест',
            'category': 'тест',
            'publisher': 'Тест',
            'book_file': self.get_pdf("dup1.pdf"),
            'book_type': 'fiction'
        }
        response1 = self.client.post('/api/books/', data)
        self.assertEqual(response1.status_code, 201)

        # новый файл, иначе будет емпти)
        data2 = {**data, 'book_file': self.get_pdf("dup2.pdf")}
        response2 = self.client.post('/api/books/', data2)
        self.assertEqual(response2.status_code, 400)
        self.assertIn('уже существует', str(response2.data).lower())

    def test_textbook_edition_logic_via_api(self):
        self.client.force_authenticate(user=self.admin)
        base = {
            'title': 'Физика. 10 кл.',
            'author': self.author.id,
            'genre': 'учебное пособие',
            'category': 'учебник',
            'book_type': 'textbook'
        }

        response1 = self.client.post('/api/books/', {
            **base,
            'year': 2020,
            'publisher': 'Просвещение',
            'book_file': self.get_pdf("phys1.pdf")
        })
        self.assertEqual(response1.status_code, 201)

        response2 = self.client.post('/api/books/', {
            **base,
            'year': 2020,
            'publisher': 'Просвещение',
            'book_file': self.get_pdf("phys2.pdf")
        })
        self.assertEqual(response2.status_code, 400)

        response3 = self.client.post('/api/books/', {
            **base,
            'year': 2022,
            'publisher': 'Просвещение',
            'book_file': self.get_pdf("phys3.pdf")
        })
        self.assertEqual(response3.status_code, 201)

        response4 = self.client.post('/api/books/', {
            **base,
            'year': 2020,
            'publisher': 'Дрофа',
            'book_file': self.get_pdf("phys4.pdf")
        })
        self.assertEqual(response4.status_code, 201)

        self.assertEqual(Book.objects.filter(title='Физика. 10 кл.').count(), 3)