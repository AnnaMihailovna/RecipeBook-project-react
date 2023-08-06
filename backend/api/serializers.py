from django.contrib.auth import get_user_model
from drf_base64.fields import Base64ImageField
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (
    # FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    # RecipeShoppingList,
    # RecipeTag,
    Tag
)
from users.models import Follow

User = get_user_model()


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
        # return Follow.objects.filter(user=self.context['request'].user,
        #                              author=obj).exists()
        return obj.following.filter(user=request.user).exists()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор для работы с моделью тегов."""
    class Meta:
        model = Tag
        fields = ('__all__')
        read_only_fields = (fields,)


class IngredientSerializer(serializers.ModelSerializer):
    '''Сериализатор для работы с моделью ингредиента.'''

    class Meta:
        model = Ingredient
        fields = ('__all__')
        read_only_fields = (fields,)


class RecipeShortSerializer(serializers.ModelSerializer):
    """
    Cериализатор модели Recipe для краткого
    отображения на страницах со списками.
    """
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('title', 'image', 'author', 'scook_time')


class RecipeSerializer(serializers.ModelSerializer):
    """
    Основной сериализатор модели Recipe для полного его
    отображения.
    """
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_list = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'title', 'image', 'text', 'cook_time')
    
    @staticmethod
    def get_ingredients(obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return IngredientAddRecipeSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        """Проверка на наличие рецепта в избранном."""
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return object.elected.filter(user=request.user).exists()
    
    def get_is_in_shopping_list(self, obj):
        """Проверка на наличие рецепта в списке покупок."""
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return object.shopping.filter(user=request.user).exists()


class IngredientAddRecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для добавления ингредиентов в рецепт.
    """
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField()
    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления и обновления рецепта."""
    ingredients = IngredientAddRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        error_messages={'does_not_exist': 'Указанного тега не существует'},
        many=True
    )
    image = Base64ImageField()
    # title = serializers.CharField(max_length=200)
    # cook_time = serializers.IntegerField()
    author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Recipe
        # fields = ('id', 'ingredients', 'tags',
        #           'image', 'title', 'text',
        #           'cook_time', 'author')
        fields = ('__all__')

    def validate_ingredients(self, ingredients):
        """Проверка ингредиентов."""
        if not ingredients:
            raise ValidationError(
                'Необходимо выбрать ингредиенты!'
            )
        return ingredients
    
    def validate_cook_time(value):
        if value <= 0:
            raise ValidationError(
                'Время приготовления должно быть больше нуля!'
            )
        return value
    
    def add_ingredients(self, recipe, ingredients):
        """Добавление ингредиентов в рецепт."""
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient=ingredient['ingredient'],
                amount=ingredient['amount']
            ) for ingredient in ingredients
        )
    
    def create(self, validated_data):
        """"Добавление рецепта."""
        author = self.context.get('request').user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        image = validated_data.pop('image')
        recipe = Recipe.objects.create(image=image, author=author,
                                       **validated_data)
        recipe.tags.set(tags)
        self.add_ingredients(recipe, ingredients)
        return recipe
    
    def update(self, recipe, validated_data):
        """"Обновление рецепта."""
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        recipe.tags.set(tags)
        self.add_ingredients(recipe, ingredients)
        return super().update(recipe, validated_data)
    
    def to_representation(self, recipe):
        """
        Отображает новый или обновленный рецепт
        через полный сериализатор RecipeSerializer.
        """
        context = {'request': self.context.get('request')}
        return RecipeSerializer(recipe, context=context).data


class SubscribedSerializer(CustomUserSerializer):
    """Сериализатор для работы с подписками."""
    recipes = serializers.SerializerMethodField(read_only=True)
    recipes_count = serializers.SerializerMethodField(read_only=True)

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + ('recipes_count', 'recipes')
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

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
    '''Сериализатор для модели Follow.'''
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


