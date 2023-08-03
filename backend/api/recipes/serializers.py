from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import validators
from rest_framework.exceptions import PermissionDenied
from rest_framework.serializers import (
    BooleanField, IntegerField, ModelSerializer,
    PrimaryKeyRelatedField, SerializerMethodField, ReadOnlyField,
    ValidationError
)

from api.users.serializers import UserSerializer
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.models import Subscription


User = get_user_model()


class TagSerializer(ModelSerializer):
    """
    Сериализатор, созданный для модели "Tag", с определенным набором полей,
    включая проверку уникальности.
    """

    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class IngredientSerializer(ModelSerializer):
    """Сериализатор, созданный для модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'unit_of_measurement',)


class RecipeIngredientSerializer(ModelSerializer):
    """
    Сериализатор для модели "RecipeIngredient" с набором полей
    для получения информации об ингредиентах в рецепте.
    """
    id = ReadOnlyField(source='ingredient.id')
    name = ReadOnlyField(source='ingredient.name')
    unit_of_measurement = ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'unit_of_measurement', 'amount', )


class RecipeIngredientCreateSerializer(ModelSerializer):
    """Сериализатор, предназначенный для добавления ингредиентов в рецепт."""
    id = IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount', )


class RecipeSerializer(ModelSerializer):
    """Сериализатор для модели Recipe, предназначенный для "GET" запросов."""
    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True, read_only=True, source='recipe_ingredients'
    )
    image = Base64ImageField()
    is_favorited = BooleanField(read_only=True, default=False)
    is_in_shopping_cart = BooleanField(read_only=True, default=False)

    class Meta:
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )
        model = Recipe


class RecipePostSerializer(ModelSerializer):
    """
    Сериализатор для модели "Recipe" и предназначенный для обработки "POST"
    запросов. В нем определены необходимые поля и методы для создания,
    редактирования рецепта и добавления ингредиентов в него.
    """
    tags = PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    ingredients = RecipeIngredientCreateSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'author', 'ingredients', 'tags',
            'image', 'name', 'text', 'cooking_time',
        )

    def validate_ingredients(self, ingredients):
        """Функция проверяет наличие хотя бы одного ингредиента,
        также проверяет уникальность ингредиента в рецепте,
        и чтобы количество ингредиентов было больше нуля.
        """
        if not ingredients:
            raise ValidationError(
                'Необходимо добавить хотя бы один ингредиент'
            )
        ingredients_list = [ingredient['id'] for ingredient in ingredients]
        if len(ingredients_list) != len(set(ingredients_list)):
            raise ValidationError(
                'Ингредиенты не должны повторяться'
            )
        for ingredient in ingredients:
            if int(ingredient['amount']) <= 0:
                raise ValidationError({
                    'Количество ингредиента не может быть равно нулю'
                })
        return ingredients

    def validate_tags(self, tags):
        """Функция проверяет наличие хотя бы одного тега."""
        if not tags:
            raise ValidationError(
                'Необходимо добавить хотя бы один тэг'
            )
        if len(tags) != len(set(tags)):
            raise ValidationError(
                'Теги не должны повторяться'
            )
        return tags

    @transaction.atomic
    def add_ingredients(self, recipe, ingredients):
        """Функция добавления ингредиентов в рецепт, выполняется атомарно."""
        ingredient_list_in_recipe = []
        for ingredient_data in ingredients:
            ingredient_list_in_recipe.append(
                RecipeIngredient(
                    ingredient=get_object_or_404(Ingredient,
                                                 id=ingredient_data['id']),
                    amount=ingredient_data['amount'],
                    recipe=recipe,
                )
            )
        RecipeIngredient.objects.bulk_create(ingredient_list_in_recipe)

    @transaction.atomic
    def create(self, validated_data):
        """Функция создания рецепта с ингредиентами, выполняется атомарно."""
        request = self.context.get('request')
        author = request.user
        if not request.user.is_authenticated:
            raise PermissionDenied(
                detail='Вы должны быть зарегистрированы, чтобы создать рецепт.'
            )
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self.add_ingredients(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, recipe, validated_data):
        """Функция редактирования рецепта, выполняется атомарно."""
        tags = validated_data.pop('tags')
        if tags is not None:
            recipe.tags.clear()
            recipe.tags.set(tags)
        ingredients = validated_data.pop('ingredients')
        if ingredients is not None:
            RecipeIngredient.objects.filter(recipe=recipe).delete()
            self.add_ingredients(recipe, ingredients)
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        """Из функции возвращаются сериализованные данные."""
        return RecipeSerializer(instance, context=self.context).data


class RecipeShortSerializer(ModelSerializer):
    """Мини сериализатор для рецепта, который используется при добавлении
    в избранное и подписках.
    """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FavoriteRecipeSerializer(ModelSerializer):
    """
    Сериализатор для модели "Favorite", содержит в себе определенный набор
    полей и метод для определения рецепта, который находится в корзине покупок.
    """

    class Meta:
        model = Favorite
        fields = ('user', 'recipe',)
        validators = [
            validators.UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=['user', 'recipe'],
            )
        ]

    def create(self, validated_data):
        """Создается экземпляр модели "Favorite"."""
        return Favorite.objects.create(**validated_data)


class ShoppingCartSerializer(ModelSerializer):
    """Сериализатор модели "ShoppingCart"."""

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe',)


class UserSubscribeSerializer(ModelSerializer):
    """Сериализатор для модели User."""
    is_subscribed = SerializerMethodField()
    recipes = RecipeShortSerializer(many=True)
    recipes_count = ReadOnlyField(source='author.recipes.count')

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'recipes_count', 'is_subscribed', 'recipes',)

    def validate(self, data):
        """Эта функция применяется для исключения подписки на самого себя."""
        request = self.context.get('request')
        author = self.instance
        if request.user == author:
            raise ValidationError(
                'Вы не можете подписаться на самого себя.'
            )
        return data

    def get_is_subscribed(self, obj):
        """Это функция, которая определяет наличия подписки на юзера."""
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscription.objects.filter(
            user=request.user, author=obj
        ).exists()

    def get_recipes_count(self, obj):
        """Функция возвращает количество рецептов."""
        return obj.recipes.count
