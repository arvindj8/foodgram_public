from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)


@admin.register(Tag)
class TagsAdmin(admin.ModelAdmin):
    """Админка для тегов."""
    list_display = ('id', 'name', 'color', 'slug')
    list_filter = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админка для ингредиентов."""
    list_display = ('id', 'name', 'unit_of_measurement')
    search_fields = ('name',)
    list_filter = ('name', 'unit_of_measurement')

    def unit_of_measurement(self, obj):
        """Возвращает единицу измерения для ингредиента."""
        return obj.unit_of_measurement
    unit_of_measurement.short_description = 'Единица измерения'


class RecipeIngredientAdmin(admin.TabularInline):
    model = RecipeIngredient
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админка рецептов."""
    list_display = (
        'id',
        'name',
        'author',
        'text',
        'cooking_time',
        'pub_date',
    )
    inlines = (RecipeIngredientAdmin,)
    search_fields = ('name',)
    list_filter = ('author', 'name', 'tags',)
    readonly_fields = ('favorites',)

    def favorites(self, obj):
        """Возвращает количество юзеров, добавивших рецепт в избранное."""
        return obj.favorite.count()


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """Админка корзины."""
    list_display = ('id', 'user', 'recipe',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админка избранного."""
    list_display = ('id', 'user', 'recipe',)
