from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.permissions import IsAuthor
from api.pagination import MyPaginator
from recipes.models import (Favorite, Ingredient, Recipe,
                            ShoppingCart, Tag)

from .filters import IngredientFilter, RecipeFilter
from .serializers import (FavoriteRecipeSerializer, IngredientSerializer,
                          RecipePostSerializer, RecipeSerializer,
                          ShoppingCartSerializer, TagSerializer)
from .services import get_shopping_list

User = get_user_model()


class TagViewSet(ReadOnlyModelViewSet):
    """Представление только для чтения информации о тегах."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(ReadOnlyModelViewSet):
    """Представление только для чтения информации об ингредиентах."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = IngredientFilter
    search_fields = ('^name', 'name')


class RecipeViewSet(ModelViewSet):
    """
    Представление для получения, создания, изменения и удаление рецептов.
    """
    permission_classes = (IsAuthor, )
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    pagination_class = MyPaginator

    def get_serializer_class(self):
        """Функция для определения класса сериализатора."""
        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipePostSerializer

    def get_queryset(self):
        """Функция для получения списка рецептов."""
        queryset = (
            Recipe.objects
            .select_related('author')
            .prefetch_related('ingredients', 'tags')
        )
        user = self.request.user

        if user.is_authenticated:
            favorite_qs = Favorite.objects.filter(
                user=user, recipe=OuterRef('id')
            )
            shopping_cart_qs = ShoppingCart.objects.filter(
                user=user, recipe=OuterRef('id')
            )
            queryset = queryset.annotate(
                is_favorited=Exists(favorite_qs),
                is_in_shopping_cart=Exists(shopping_cart_qs)
            )

        return queryset

    def add_to_list(self, request, pk, serializer_class):
        """Функция для добавления объекта в список."""
        context = {'request': request}
        recipe = get_object_or_404(Recipe, id=pk)
        data = {
            'user': request.user.id,
            'recipe': recipe.id
        }
        serializer = serializer_class(data=data, context=context)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=HTTPStatus.CREATED)

    def remove_from_list(self, request, pk, Model, message):
        """Функция для удаления рецепта из списка."""
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        Model.objects.filter(user=user,
                             recipe=recipe).delete()

        return Response({'status': message}, status=HTTPStatus.OK)

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        """Функция для добавления рецепта в корзину."""
        return self.add_to_list(request, pk, ShoppingCartSerializer)

    @shopping_cart.mapping.delete
    def remove_from_cart(self, request, pk):
        """Функция для удаления рецепта из корзины."""
        return self.remove_from_list(request,
                                     pk,
                                     ShoppingCart,
                                     'Рецепт удален из корзины')

    @action(
        detail=True,
        methods=['POST'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        """Функция для добавления рецепта в избранное."""
        return self.add_to_list(request, pk, FavoriteRecipeSerializer)

    @favorite.mapping.delete
    def remove_from_favorite(self, request, pk):
        """Функция для удаления рецепта из избранного."""
        return self.remove_from_list(request, pk, Favorite,
                                     'Рецепт удален из списка избранных')

    @action(
        methods=['GET'],
        detail=False,
        permission_classes=[IsAuthenticated],
    )
    def download_shopping_cart(self, request):
        """Функция для скачивания полного списка покупок."""
        user = request.user
        shopping_list = get_shopping_list(user)

        return HttpResponse(
            shopping_list,
            {
                "Content-Type": "text/plain",
                "Content-Disposition": "attachment; filename='shop_list.txt'",
            },
        )
