from django_filters.rest_framework import (BooleanFilter, FilterSet, filters,
                                           ModelMultipleChoiceFilter)

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(FilterSet):
    """Фильтруем ингредиенты на сайте"""
    name = filters.CharFilter(lookup_expr='startswith')

    class Meta:
        model = Ingredient
        fields = ['name']


class RecipeFilter(FilterSet):
    """
    Фильтруем рецепты по автору, тегам, а также по наличию в избранном
    и корзине юзера.
    """
    tags = ModelMultipleChoiceFilter(
        queryset=Tag.objects.all(),
        field_name='tags__slug',
        to_field_name='slug'

    )
    is_favorited = BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = BooleanFilter(
        method='filter_shopping_cart'
    )

    def filter_is_favorited(self, queryset, name, value):
        """Фильтр определяет, добавлен ли рецепт в избранное юзера."""
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(favorite__user=user)

        return queryset

    def filter_shopping_cart(self, queryset, name, value):
        """Фильтр определяет, добавлен ли рецепт в корзину юзера."""
        user = self.request.user
        if value and user.is_authenticated:
            return queryset.filter(shopping_list__user=user)

        return queryset

    class Meta:
        model = Recipe
        fields = ['author', 'tags', 'is_favorited', 'is_in_shopping_cart']
