from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CustomUserViewSet # IngredientViewSet, RecipeViewSet, TagViewSet, 

app_name = 'api'

router = DefaultRouter()
# router.register(r'ingredients', IngredientViewSet, basename='ingredients')
# router.register(r'tags', TagViewSet, basename='tags')
# router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'users', CustomUserViewSet, basename='users')
router.register(r'users/<int:pk>/subscribe/', CustomUserViewSet, basename='users_subscribe')


urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
