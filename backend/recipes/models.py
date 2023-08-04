from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

LEN_OF_STR_METHOD_IN_RECIPE = 50

User = get_user_model()

class Tag(models.Model):
    """Модель тегов."""
    name = models.CharField(
        max_length=50,
        verbose_name='Название тега',
        unique=True,
        help_text='Название тега',
    )
    color = ColorField(
        default='#FF0000',
        verbose_name='Цвет в HEX',
        unique=True,
        help_text='Выберите цвет',
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        unique=True,
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'color',),
                name='unique_tags'
            )
        ]

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов."""
    name = models.CharField(
        verbose_name='Название',
        max_length=200,
        help_text='Введите название ингредиента',
        db_index=True,
    )
    unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=50,
        help_text='Выберите единицу измерения',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'unit',),
                name='unique_unit_ingredient'),
        )
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name} {self.unit}'


class Recipe(models.Model):
    """Модель рецептов."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта',
        help_text='Автор рецепта',
    )
    title = models.CharField(
        verbose_name='Название рецепта',
        max_length=200,
        unique=True,
        help_text='Укажите название рецепта',
    )
    image = models.ImageField(
        verbose_name='Фото блюда',
        upload_to='recipes/',
        help_text='Загрузите фото готового блюда',
    )
    description = models.TextField(verbose_name='Описание рецепта')
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipe',
        verbose_name='Ингредиенты рецепта',
        help_text='Выберите нужные ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        through='RecipeTag',
        verbose_name='Теги',
        related_name='recipe',
        help_text='Выберите теги',
    )
    cook_time = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(
            1,
            message='Время не менее 1 минуты!',
        ),),
        verbose_name='Время приготовления',
        help_text='Укажите время приготовления блюда в минутах',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.title}[:LEN_OF_STR_METHOD_IN_RECIPE]'


class RecipeIngredient(models.Model):
    """Модель, связывающая рецепты с ингредиентами."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    amount = models.PositiveSmallIntegerField(
        validators=(MinValueValidator(
            1,
            message='Укажите количество не меньше 1!',
        ),),
        verbose_name='Количество единиц ингредиента',
        help_text='Введите количество больше нуля',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient',),
                name='unique_ingredients_in_recipe'),
        )
        verbose_name = 'Связь рецепта с ингредиентом'
        verbose_name_plural = 'Связи рецептов с ингредиентами'

    def __str__(self):
        return (
            f'Ингредиент {self.ingredient.name} в рецепте {self.recipe} - '
            f'{self.amount} {self.ingredient.unit}'
        )

class RecipeTag(models.Model):
    """Модель связи рецепта и тега."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        verbose_name='Тег',
    )
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('recipe', 'tag',),
                name='unique_tag_for_recipe',
            ),
        ]
        verbose_name = 'Связь рецепта с тегом'
        verbose_name_plural = 'Связи рецептов с тегами'

    def __str__(self):
        return f'Тег {self.tag} в рецепте {self.recipe}'


class FavoriteRecipe(models.Model):
    """Модель рецептов избранного списка."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='elected',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='elected',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe',),
                name='unique_elected',
            ),
        )
        ordering = ('-id',)
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return (
            f'Рецепт {self.recipe} в избранном списке '
            f'пользователя {self.user}'
        )


class RecipeShoppingList(models.Model):
    """Модель рецептов для списка покупок."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shopping'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe',),
                name='unique_shopping_pair',
            ),
        )
        ordering = ('-id',)
        verbose_name = 'Рецепт для списка покупок'
        verbose_name_plural = 'Рецепты для списков покупок'

    def __str__(self):
        return (
            f'У пользователя {self.user} рецепт {self.recipe} '
            f'в списке покупок'
        )
