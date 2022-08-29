from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase


User = get_user_model()


class ErrorPage(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='Test_user')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        

    # Ошибка 404 ---------------------------------------------------
    def test_page_not_founded(self):
        response = self.authorized_client.get('/NotKnownPage/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
