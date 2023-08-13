from django.contrib import admin

from recipes.models import (
    FavoriteRecipe,
    Ingredient,
    Recipe,
    RecipeIngredient,
    RecipeShoppingList,
    RecipeTag,
    Tag
)


class TagAdmin(admin.ModelAdmin):
    """Отображение модели тегов в админке."""
    list_display = (
        'id',
        'name',
        'color',
        'slug',
    )


class IngredientAdmin(admin.ModelAdmin):
    """Отображение модели ингредиентов в админке."""
    list_display = (
        'name',
        'unit',
    )
    list_filter = ('name',)
    search_fields = ('name',)
    ordering = ('name',)
    empty_value_display = '-пусто-'


class RecipeIngredientsInline(admin.TabularInline):
    model = RecipeIngredient
    min_num = 1
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    """Отображение модели рецептов в админке."""
    list_display = (
        'id',
        'name',
        'author',
        'pub_date',
        'elected',
    )
    list_filter = ('name', 'author', 'tags',)
    readonly_fields = ('elected',)
    inlines = (RecipeIngredientsInline,)
    empty_value_display = '-пусто-'

    def elected(self, obj):
        """
        Общее число добавлений рецепта в избранное.
        """
        return obj.elected.all().count()


class FavoriteRecipeAdmin(admin.ModelAdmin):
    """
    Отображение модели избранных пользователем
    рецептов в админке.
    """
    list_display = ('id', 'user', 'recipe',)
    empty_value_display = '-пусто-'


class RecipeShoppingListAdmin(admin.ModelAdmin):
    """
    Отображение модели рецептов из списка покупок в админке.
    """
    list_display = ('id', 'user', 'recipe',)
    empty_value_display = '-пусто-'


class RecipeIngredientsAdmin(admin.ModelAdmin):
    """
    Отображение вспомогающей модели связи рецептов
    и ингредиентов в админке.
    """
    list_display = ('id', 'recipe', 'ingredient', 'amount',)
    list_filter = ('recipe', 'ingredient')


class RecipeTagAdmin(admin.ModelAdmin):
    """
    Отображение вспомогающей модели связи рецептов
    и тегов в админке.
    """
    list_display = ('id', 'recipe', 'tag',)
    list_filter = ('recipe', 'tag',)


admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(FavoriteRecipe, FavoriteRecipeAdmin)
admin.site.register(RecipeShoppingList, RecipeShoppingListAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientsAdmin)
admin.site.register(RecipeTag, RecipeTagAdmin)
