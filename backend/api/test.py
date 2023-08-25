from http import HTTPStatus

from django.test import Client, TestCase

from recipes.models import Recipe
from users.models import User


class RecipeBookAPITestCase(TestCase):
    def setUp(self):
        # self.guest_client = Client()
        self.user = User.objects.create_user(email='admin')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_list_exists(self):
        """Проверка доступности списка рецептов."""
        response = self.authorized_client.get('/api/recipes/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_recipe_creation(self):
        """Проверка создания рецепта."""
        data = {"email": "vpupkin@yandex.ru",
                "username": "vasya.pupkin",
                "first_name": "Вася",
                "last_name": "Пупкин",
                "password": "Qwerty123"}
        response = self.authorized_client.post('/api/pecipe/', data=data)
        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertTrue(
            Recipe.objects.filter(username='vasya.pupkin').exists()
        )
