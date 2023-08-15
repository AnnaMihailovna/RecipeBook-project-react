from django.contrib.auth.hashers import make_password
from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import (
    CustomUserSerializer,
    FavoriteRecipeSerializer,
    IngredientSerializer,
    RecipeCreateUpdateSerializer,
    RecipeSerializer,
    RecipeShoppingListSerializer,
    SubscriptionsSerializer,
    TagSerializer
)
from .filters import IngredientFilter, RecipeFilter
from .permissions import AuthorOnly
from recipes.models import Ingredient, Recipe, Tag
from users.models import Follow, User
from .services import get_ingredients


class CustomUserViewSet(UserViewSet):
    """
    Вьюсет обработки всех запросов
    пользователей и  подписок.
    """
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    @action(methods=['POST'],
            detail=False,
            permission_classes=[permissions.IsAuthenticated])
    def set_password(self, request):
        """
        Обрабатка эндпоинта '/set_password' -
        изменение пароля.
        """
        user = self.request.user
        if user.is_anonymous:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        new_password = request.data.get('new_password')
        if not new_password:
            return Response(
                {'error': '"new_password": обязательное поле для заполнения'},
                status=status.HTTP_400_BAD_REQUEST)
        user.password = make_password(new_password)
        user.save()
        return Response({'status': 'password set'})

    @action(methods=['POST', 'DELETE'], detail=True,
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, id):
        """
        Авторизированный пользователь
        добавляет/удалет подписку на другого пользователя.
        """
        user = request.user
        author = get_object_or_404(User, id=id)
        subscription = Follow.objects.filter(user=user, author=author)
        if request.method == 'POST':
            if subscription.exists():
                return Response({'error': f'Вы уже подписаны на {author}'},
                                status=status.HTTP_400_BAD_REQUEST)
            if user == author:
                return Response({'error': 'Невозможно подписаться на себя'},
                                status=status.HTTP_400_BAD_REQUEST)
            serializer = SubscriptionsSerializer(
                author,
                context={'request': request})
            Follow.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if subscription.exists():
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'error': f'Вы не подписаны на пользователя {author}'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['GET'],
            detail=False,
            permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        """
        Авторизированный пользователь
        получает список своих подписок.
        """
        subscriptions = User.objects.filter(
            following__user=self.request.user
        )
        page = self.paginate_queryset(subscriptions)
        serializer = SubscriptionsSerializer(
            page, many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Вся работа с рецептами: детально и в списках.
    Списки рецептов: главный, избранное, корзина;
    добавление, удаление и изменение рецептов в
    этих списках; скачивание файла.
    """
    queryset = Recipe.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = RecipeCreateUpdateSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_permissions(self):
        """
        Просмотр списка рецептов и списка по id
        доступен всем.
        """
        if self.action in ['list', 'retrieve']:
            return (permissions.AllowAny(),)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipeCreateUpdateSerializer

    def _action_post_delete(self, pk, serializer_class):
        """
        Функция для добавления/удаления рецепта в списки.
        """
        user = self.request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        object = serializer_class.Meta.model.objects.filter(
            user=user,
            recipe=recipe
        )
        if self.request.method == 'POST':
            data = {'user': user.id, 'recipe': pk}
            context = {'request': self.request}
            serializer = serializer_class(data=data,
                                          context=context)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if object.exists():
            object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'Этого рецепта не было в cписке'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            permission_classes=[permissions.IsAuthenticated],
            methods=['POST', 'DELETE'])
    def favorite(self, request, pk=None):
        """Добавляет/удаляет рецепт в список избранного."""
        return self._action_post_delete(pk, FavoriteRecipeSerializer)

    @action(detail=True,
            permission_classes=[permissions.IsAuthenticated],
            methods=['POST', 'DELETE'], )
    def shopping_cart(self, request, pk=None):
        """Добавляет/удаляет рецепт в список покупок."""
        return self._action_post_delete(pk, RecipeShoppingListSerializer)

    @action(detail=False, permission_classes=[AuthorOnly])
    def download_shopping_cart(self, request):
        """Загружает .txt файл со списком покупок."""
        ingredients = get_ingredients(request.user)
        shopping_list = 'Список покупок:'
        for ingredient in ingredients:
            shopping_list += (
                f"\n- {ingredient[0]} "
                f"({ingredient[1]}) - "
                f"{ingredient[2]}")
        file = 'shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{file}.txt"'
        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вывод тегов."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вывод ингредиентов."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny,)
    filter_backends = (IngredientFilter,)
    search_fields = ('^name', )
