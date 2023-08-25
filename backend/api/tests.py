from http import HTTPStatus

from django.test import Client, TestCase

# from recipes.models import Recipe
# from users.models import User


class RecipeBookAPITestCase(TestCase):
    def setUp(self):
        self.guest_client = Client()
        # self.user = User.objects.create_user(email="vpupkin@yandex.ru",
        #                                      username="vasya.pupkin",
        #                                      first_name="Вася",
        #                                      last_name="Пупкин",
        #                                      password="Qwerty123"
        #                                      )
        # self.authorized_client = Client()
        # self.authorized_client.force_login(self.user)

    def test_list_exists(self):
        """Проверка доступности списка рецептов."""
        response = self.guest_client.get('/api/recipes/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    # def test_recipe_creation(self):
    #     """Проверка создания рецепта."""
    #     data = {"ingredients": [{}],
    #             "tags": [],
    #             "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEU\
    #             gAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAA\
    #             CXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAA\
    #             ggCByxOyYQAAAABJRU5ErkJggg==",
    #             "name": "string",
    #             "text": "string",
    #             "cooking_time": 1}
    #     response = self.authorized_client.post('/api/pecipe/', data=data)
    #     self.assertEqual(response.status_code, HTTPStatus.CREATED)
    #     self.assertTrue(
    #         Recipe.objects.filter(username='vasya.pupkin').exists()
    #     )
