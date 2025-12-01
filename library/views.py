from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter
from .models import Author, Book
from .serializers import AuthorSerializer, BookSerializer


# класс реализующий методы
class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()     # возвращает всех авторов
    serializer_class = AuthorSerializer
    permission_classes = [permissions.IsAdminUser]         # права доступа
    filter_backends = [SearchFilter]
    search_fields = ['name', 'biography']

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:          # просмотр доступен всем
            return [permissions.AllowAny()]
        return super().get_permissions()


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.select_related('author').all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [SearchFilter]
    search_fields = ['title', 'genre', 'category', 'publisher', 'author__name']

    # доступно всем 'list', 'retrieve'
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return super().get_permissions()