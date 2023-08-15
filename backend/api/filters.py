from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from recipes.models import Ingredient, Recipe, Tag


class IngredientFilter(SearchFilter):
    """Поиск ингредиентов по названию."""
    search_param = 'name'

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(FilterSet):
    """Фильтр рецептов по автору, тегу,
    наличию в избранном и в списке покупок.
    """
    author = filters.AllValuesMultipleFilter(
        field_name='author__id',
    )
    is_favorited = filters.BooleanFilter(
        method='get_is_favorited',
        label='favorite',
    )
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart',
        label='shopping_cart',
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_is_favorited(self, queryset, name, value):
        """Рецепты, находящиеся в списке избранного."""
        if value:
            return queryset.filter(
                elected__user=self.request.user
            )
        return queryset.exclude(
            elected__user=self.request.user
        )

    def get_is_in_shopping_cart(self, queryset, name, value):
        """Рецепты, находящиеся в списке покупок."""
        if value:
            return Recipe.objects.filter(
                shopping__user=self.request.user
            )
