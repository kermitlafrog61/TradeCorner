from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from knox.models import AuthToken

User = get_user_model()


def create_test_user():
    user = User.objects.create_user(
            username='testuser', email='testuser@example.com',
            password='testpass', is_active = True,
            activation_code='test-code'
    )
    return user



class RegistrationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_registration(self):
        response = self.client.post('/accounts/registration/', {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpass',
            'password_confirm': 'testpass'
        })

        self.assertEqual(response.status_code, 201)
        user = User.objects.get(username='testuser')
        self.assertEqual(user.email, 'testuser@example.com')
        self.assertFalse(user.is_active)


class ActivateTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_test_user()
        self.user.is_active = False
        self.activation_url = reverse(
            'activate', args=[self.user.activation_code])

    def test_activation(self):
        response = self.client.get(self.activation_url)

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)


class LoginTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_test_user()

    def test_login(self):
        for i in range(2):
            responce = self.client.post('/accounts/login/', {
                'username': 'testuser',
                'password': 'testpass'
            })
            self.assertEqual(responce.status_code, 200)

        failed_responce = self.client.post('/accounts/login/', {
            'username': 'testuser',
            'password': 'testpass'
        })
        self.assertEqual(failed_responce.status_code, 403)


class PwdUpdateTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_test_user()
        self.token = AuthToken.objects.create(self.user)[1]
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def test_update(self):
        responce = self.client.patch('/accounts/change-password/', {
            'old_pwd': 'testpass',
            'new_pwd': 'testpass2',
            'new_pwd_conf': 'testpass2'
        })
        self.assertEqual(responce.status_code, 200)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('testpass2'))

class PwdRestoreTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_test_user()
        self.token = AuthToken.objects.create(self.user)[1]
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def test_update(self):
        responce = self.client.patch('/accounts/restore-password/', {
            'activation_code': 'test-code',
            'new_pwd': 'testpass2',
            'new_pwd_conf': 'testpass2'
        })
        self.assertEqual(responce.status_code, 200)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('testpass2'))    
