from django.core.exceptions import ValidationError as DjangoValidationError
import rest_framework
from rest_framework.exceptions import ValidationError
from .models import Author, Book
import mimetypes

class AuthorSerializer(serializers.ModelSerializer):
    books = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = ['id', 'name', 'biography', 'books']

    def get_books(self, obj):
        return [
            {"id": book.id, "title": book.title}
            for book in obj.books.all()
        ]


def validate_book_file(file):
    mime_type, _ = mimetypes.guess_type(file.name)
    if not mime_type:
        raise ValidationError("Не удалось определить тип файла.")

    allowed_types = ['application/pdf', 'application/epub+zip']
    if mime_type not in allowed_types:
        raise ValidationError(
            f"Недопустимый тип файла: {mime_type}. Разрешены: PDF, EPUB."
        )

    if file.size > 50 * 1024 * 1024:
        raise ValidationError("Файл слишком большой. Максимум — 50 МБ.")


class BookSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.name', read_only=True)
    cover_image = serializers.ImageField(required=False, allow_null=True)
    book_file = serializers.FileField(validators=[validate_book_file])

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'author_name', 'year', 'genre',
            'category', 'publisher', 'cover_image', 'book_file',
            'book_type'
        ]
        # author — для записи (ID), author_name — для чтения

    def validate_year(self, value):
        if not (1000 <= value <= 9999):
            raise serializers.ValidationError("Год должен быть в диапазоне от 1000 до 9999.")
        return value

    def validate(self, data):
        title = data.get('title')
        author = data.get('author')
        year = data.get('year')
        publisher = data.get('publisher')

        if all([title, author, year, publisher]):
            queryset = Book.objects.filter(
                title=title,
                author=author,
                year=year,
                publisher=publisher
            )
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)

            if queryset.exists():
                raise ValidationError({
                    'non_field_errors': [
                        "Книга с таким названием, автором, годом и издательством уже существует."
                    ]
                })

        return data

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except DjangoValidationError as e:
            raise ValidationError(e.message_dict)