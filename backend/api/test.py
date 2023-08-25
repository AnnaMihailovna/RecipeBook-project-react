from http import HTTPStatus

from django.test import Client, TestCase

# from users.models import User


class RecipeBookAPITestCase(TestCase):
    def setUp(self):
        self.guest_client = Client()
        # self.user = User.objects.create_user(email='admin')
        # self.authorized_client = Client()
        # self.authorized_client.force_login(self.user)

    def test_list_exists(self):
        """Проверка доступности списка рецептов."""
        response = self.guest_client.get('/api/recipes/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    # def test_recipe_creation(self):
    #     """Проверка создания рецепта."""
    #     data = {'title': 'Test', 'description': 'Test'}
    #     response = self.guest_client.post('/api/tasks/', data=data)
    #     self.assertEqual(response.status_code, HTTPStatus.CREATED)
    #     self.assertTrue(models.Task.objects.filter(title='Test').exists())
