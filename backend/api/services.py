from django.db.models import F, Sum

from recipes.models import RecipeIngredient


def get_ingredients(user):
    """
    Cуммирование одинаковых ингредиентов
    из разных рецептов для списка покупок.
    """
    ingredients = RecipeIngredient.objects.filter(
        recipe__shopping__user=user).values(
        name=F('ingredient__name'),
        unit=F('ingredient__unit')
    ).annotate(amount=Sum('amount')).values_list(
        'ingredient__name', 'ingredient__unit', 'amount')
    return ingredients
