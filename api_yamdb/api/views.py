from django.db.models.aggregates import Avg
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Genre, Review, Title, User

from .filters import TitleFilter
from .mixins import CustomMixin
from .permissions import (IsAdminModerAuthorOrReadOnly, IsAdminOrReadOnly,
                          UserMeOrAdmin)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, GetTokenSerializer, MeSerializer,
                          ReviewSerializer, SignUpSerializer,
                          TitleReadSerializer, TitleWriteSerializer,
                          UsersSerializer)
from .utils import send_email


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def auth_signup(request):
    """
    Отправляет код подтверждения на переданный email. Авторизация не требуется.
    Запрещено использовать значение 'me' в качестве имени пользователя.
    Поля email и username должны быть уникальными.
    """
    serializer = SignUpSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    email_body = (
        f'Приветствуем Вас, {user.username}!'
        '\nДля завершения регистрации в сервисе YaMDB'
        f' укажите данный проверочный код: {user.confirmation_code}'
    )
    data = {
        'email_body': email_body,
        'to_email': user.email,
        'email_subject': 'Код подтверждения для доступа к API!'
    }
    send_email(data)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def get_auth_token(request):
    """
    Получение JWT-токена при соответствии username и confirmation code.
    Авторизация не требуется
    """
    serializer = GetTokenSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data
    try:
        user = User.objects.get(username=data['username'])
    except User.DoesNotExist:
        return Response(
            {'username': 'Пользователь не обнаружен'},
            status=status.HTTP_404_NOT_FOUND)
    if data.get('confirmation_code') == user.confirmation_code:
        token = RefreshToken.for_user(user).access_token
        return Response({'token': str(token)},
                        status=status.HTTP_201_CREATED)
    return Response(
        {'confirmation_code': 'Предоставлен неверный код подтверждения'},
        status=status.HTTP_400_BAD_REQUEST)


class UsersViewSet(viewsets.ModelViewSet):
    """
    Получение данных о пользователях. Доступно для роли Администратор
    Для аутентифицированных пользователей для редактирования собственных данных
    доступен эндпоинт /users/me/
    """
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (UserMeOrAdmin,)
    lookup_field = 'username'
    filter_backends = (SearchFilter, )
    search_fields = ('username', )

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
        url_path='me')
    def get_current_user_info(self, request):
        serializer = UsersSerializer(request.user)
        if request.method == 'PATCH':
            if request.user.is_admin:
                serializer = UsersSerializer(
                    request.user,
                    data=request.data,
                    partial=True)
            else:
                serializer = MeSerializer(
                    request.user,
                    data=request.data,
                    partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data)


class CategoryViewSet(CustomMixin):
    """
    Получение всех категорий.
    Добавление, изменение, удаление определенной категории.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    search_fields = ('name',)
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)


class GenreViewSet(CustomMixin):
    """
    Получение всех жанров.
    Добавление, изменение, удаление определенного жанра.
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    search_fields = ('name', )
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)


class TitleViewSet(viewsets.ModelViewSet):
    """
    Получение всех произведений.
    Добавление, изменение, удаление определенного произведения.
    """
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    permission_classes = (IsAdminOrReadOnly,)
    filterset_class = TitleFilter
    filterset_fields = ['name', ]

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class CommentViewSet(viewsets.ModelViewSet):
    """
    Получение всех комментариев.
    Добавление, изменение, удаление определенного комментария.
    """
    serializer_class = CommentSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsAdminModerAuthorOrReadOnly
    )

    def get_review(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title=title
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())

    def get_queryset(self):
        return self.get_review().comments.select_related('author')


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Получение всех ревью.
    Добавление, изменение, удаление определенного ревью.
    """
    serializer_class = ReviewSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsAdminModerAuthorOrReadOnly
    )

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())

    def get_queryset(self):
        return self.get_title().reviews.select_related('author')
