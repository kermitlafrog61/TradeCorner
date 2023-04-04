from django.test import TestCase
from rest_framework.test import APIClient

class UserRegistrationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_user_registration(self):
        response = self.client.post('/users/registration/', {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'testpassword'
        })

        # Check that the response status code is 201 (Created)
        self.assertEqual(response.status_code, 201)

        # Check that the user was created in the database
        from django.contrib.auth.models import User
        user = User.objects.get(username='testuser')
        self.assertEqual(user.email, 'testuser@example.com')