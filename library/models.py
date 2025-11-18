from django.db import models
from django.core.exceptions import ValidationError

class Author(models.Model):
    name = models.CharField("Имя автора", max_length=200, unique=True)
    biography = models.TextField("Биография", blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"
        ordering = ['name']


class Book(models.Model):
    TYPE_CHOICES = [
        ('fiction', 'Художественное произведение'),
        ('textbook', 'Учебник'),
    ]

    title = models.CharField("Название книги", max_length=100)
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        related_name='books',
        verbose_name="Автор"
    )
    year = models.PositiveIntegerField("Год выпуска")
    genre = models.CharField("Жанр", max_length=100)
    category = models.CharField("Категория", max_length=100)
    publisher = models.CharField("Издательство", max_length=100)
    cover_image = models.ImageField(
        "Обложка",
        upload_to='covers/',
        blank=True,
        null=True
    )
    book_file = models.FileField(
        "Файл книги",
        upload_to='books/',
        help_text="Поддерживаются PDF, EPUB"
    )
    book_type = models.CharField(
        "Тип книги",
        max_length=10,
        choices=TYPE_CHOICES,
        default='fiction'
    )

    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"
        unique_together = ('title', 'author', 'year', 'publisher')
        ordering = ['title', 'year']

    def __str__(self):
        return f"{self.title} ({self.year}) — {self.author.name}"

    def clean(self):
        super().clean()

        if self.book_type == 'textbook':
            existing = Book.objects.filter(
                title=self.title,
                author=self.author,
                publisher=self.publisher,
                book_type='textbook'
            )
            if self.pk:
                existing = existing.exclude(pk=self.pk)

            same_edition = existing.filter(year=self.year).exists()
            if same_edition:
                raise ValidationError(
                    "Учебник с таким названием, автором и издательством уже существует в этом году. "
                    "Добавление разрешено только для нового издания (изменённый год)."
                )

    def save(self, *args, **kwargs):
        self.full_clean()  # вызывает clean()
        super().save(*args, **kwargs)