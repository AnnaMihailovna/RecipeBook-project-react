from django.db import transaction
from drf_base64.fields import Base64ImageField
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeShoppingList,
    Tag
)
from users.models import Follow, User


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериализатор создания нового пользователя."""
    class Meta:
        model = User
        fields = ('__all__')

    def validate_username(self, username):
        """Валидация создания пользователя с username 'me'."""
        if username == 'me':
            raise serializers.ValidationError(
                'Пользователя с username = me создавать нельзя.',
                code=status.HTTP_400_BAD_REQUEST
            )
        return username


class CustomUserSerializer(UserSerializer):
    """Сериализатор для модели User."""
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        """Подписан ли пользователь на автора."""
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.following.filter(user=request.user).exists()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с моделью тегов."""
    class Meta:
        model = Tag
        fields = ('__all__')
        read_only_fields = (fields,)


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с моделью ингредиента."""

    class Meta:
        model = Ingredient
        fields = ('__all__')
        read_only_fields = (fields,)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор модели связи ингредиентов в рецепте.
    Для вывода ингредиентов в рецепте.
    """
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    unit = serializers.ReadOnlyField(
        source='ingredient.unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'unit',
            'amount',
        )


class RecipeShortSerializer(serializers.ModelSerializer):
    """
    Cериализатор модели Recipe для краткого
    отображения на страницах со списком покупок и подписками.
    """
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('name', 'image', 'author', 'cooking_time')


class RecipeSerializer(serializers.ModelSerializer):
    """
    Основной сериализатор модели Recipe для полного его
    отображения.
    """
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        read_only=True,
        many=True,
        source='recipeingredient_set'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        """Проверка на наличие рецепта в избранном."""
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return FavoriteRecipe.objects.filter(
            recipe=obj, user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        """Проверка на наличие рецепта в списке покупок."""
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return RecipeShoppingList.objects.filter(
            recipe=obj, user=request.user).exists()


class IngredientAddRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для добавления ингредиентов в рецепт.
    """
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient')
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для добавления/удаления
    и обновления рецепта.
    """
    ingredients = IngredientAddRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    image = Base64ImageField()
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients', 'tags',
                  'image', 'name', 'text',
                  'cooking_time', 'author')

    def validate_ingredients(self, ingredients):
        """Проверка ингредиентов."""
        if not ingredients:
            raise ValidationError(
                'Необходимо выбрать ингредиенты!'
            )
        return ingredients

    def _add_ingredients(self, recipe, ingredients):
        """Добавление ингредиентов в рецепт."""
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        )

    @transaction.atomic
    def create(self, validated_data):
        """"Добавление рецепта."""
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        image = validated_data.pop('image')
        recipe = Recipe.objects.create(image=image, author=author,
                                       **validated_data)
        recipe.tags.set(tags)
        self._add_ingredients(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, recipe, validated_data):
        """"Обновление рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        recipe.tags.set(tags)
        self._add_ingredients(recipe, ingredients)
        return super().update(recipe, validated_data)

    def to_representation(self, recipe):
        """
        Отображает новый или обновленный рецепт
        через полный сериализатор RecipeSerializer.
        """
        context = {'request': self.context.get('request')}
        return RecipeSerializer(recipe, context=context).data


class SubscriptionsSerializer(CustomUserSerializer):
    """Сериализатор для работы с подписками."""
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + (
            'recipes_count',
            'recipes'
        )
        read_only_fields = (
            'email',
            'username',
            'first_name',
            'last_name'
        )

    def get_recipes(self, obj):
        """Рецепты пользователя."""
        request = self.context.get('request')
        limit = request.query_params.get('recipes_limit')
        context = {'request': request}
        if limit:
            recipes = obj.recipes.all()[:(int(limit))]
        else:
            recipes = obj.recipes.all()
        return RecipeShortSerializer(recipes, many=True,
                                     context=context).data

    def get_recipes_count(self, obj):
        """Количество рецептов пользователя."""
        return obj.recipes.count()


class FollowSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Follow."""
    user = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    def validate(self, data):
        if self.context['request'].user == data['following']:
            raise serializers.ValidationError(
                'Подписка на самого себя невозможна.'
            )
        return data

    class Meta:
        fields = ('id', 'user', 'author')
        model = Follow
        validators = [
            UniqueTogetherValidator(
                queryset=Follow.objects.all(),
                fields=('user', 'author'),
                message='Подписка уже существует'
            )
        ]


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для работы с моделью рецепта
    в списке избранного.
    """
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(),
        write_only=True
    )

    class Meta:
        model = FavoriteRecipe
        fields = ('user', 'recipe')

    def validate(self, data):
        """Валидация при добавлении рецепта в избранное."""
        user, recipe = data['user'], data['recipe']
        if FavoriteRecipe.objects.filter(user=user,
                                         recipe=recipe).exists():
            raise ValidationError(
                'Рецепт уже добавлен в избранное!'
            )
        return data

    def to_representation(self, instance):
        """Отображение добавленного в избранное рецепта."""
        request = self.context.get('request')
        context = {'request': request}
        return RecipeSerializer(
            instance.recipe,
            context=context
        ).data


class RecipeShoppingListSerializer(serializers.ModelSerializer):
    """
    Сериализатор для работы с моделью рецепта
    в списке покупок.
    """

    class Meta:
        model = RecipeShoppingList
        fields = ('id', 'user', 'recipe')

    def validate(self, data):
        """Валидация при добавлении рецепта в список покупок."""
        user, recipe = data['user'], data['recipe']
        if RecipeShoppingList.objects.filter(user=user,
                                             recipe=recipe).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в список покупок!'
            )
        return data

    def to_representation(self, instance):
        """Отображение добавленного в список покупок рецепта."""
        request = self.context.get('request')
        context = {'request': request}
        return RecipeShortSerializer(
            instance.recipe,
            context=context
        ).data
