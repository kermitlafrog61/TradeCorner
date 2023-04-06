from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Order
from apps.products.models import Product, Category

User = get_user_model()


class OrderTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='testuser1', password='testpass123', email='test1@test.com')
        self.user2 = User.objects.create_user(
            username='testuser2', password='testpass123', email='test2@test.com')
        self.category = Category.objects.create(
            title='Test Category')
        self.product = Product.objects.create(
            title='Test Product', description='Test description',
            price=10, user=self.user1, category=self.category)
        self.order1 = Order.objects.create(
            user=self.user2, product=self.product, address='Test address 1')

    def test_create_order(self):
        self.order1.delete()
        self.client.force_authenticate(user=self.user2)
        url = ('/products/%s/order/' % self.product.id)
        data = {'address': 'Test address 3'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Order.objects.get(pk=6).user, self.user2)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_order_status(self):
        self.client.force_authenticate(user=self.user1)
        url = ('/orders/%s/' % self.order1.id)
        data = {'status': 'DELIVER'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_206_PARTIAL_CONTENT)
        self.assertEqual(Order.objects.get(
            id=self.order1.id).status, 'DELIVER')

    def test_update_order_status_with_invalid_data(self):
        self.client.force_authenticate(user=self.user2)
        url = ('/orders/%s/' % self.order1.id)
        data = {'status': 'PROCESS'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_order(self):
        self.client.force_authenticate(user=self.user2)
        url = ('/orders/%s/' % self.order1.id)
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Order.objects.count(), 1)

    def test_delete_order_with_unauthorized_user(self):
        url = ('/orders/%s/' % self.order1.id)
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Order.objects.count(), 1)


class OrderCompleteTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='testuser1', password='testpass123', email='test1@test.com')
        self.user2 = User.objects.create_user(
            username='testuser2', password='testpass123', email='test2@test.com')
        self.category = Category.objects.create(
            title='Test Category')
        self.product = Product.objects.create(
            title='Test Product', description='Test description',
            price=10, user=self.user1, category=self.category)
        self.order1 = Order.objects.create(
            user=self.user2, product=self.product,
            address='Test address 1', status='DELIVER')

    def test_order_complete(self):
        self.client.force_authenticate(user=self.user2)
        url = ('/orders/%s/complete/' % self.order1.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order1.refresh_from_db()
        self.assertEqual(self.order1.status, 'COMPLETE')

    def test_order_complete_fail(self):
        self.client.force_authenticate(user=self.user1)
        url = ('/orders/%s/complete/' % self.order1.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class OrderConfirmTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='testuser1', password='testpass123', email='test1@test.com')
        self.user2 = User.objects.create_user(
            username='testuser2', password='testpass123', email='test2@test.com')
        self.category = Category.objects.create(
            title='Test Category')
        self.product = Product.objects.create(
            title='Test Product', description='Test description',
            price=10, user=self.user1, category=self.category)
        self.order1 = Order.objects.create(
            user=self.user2, product=self.product,
            address='Test address 1')

    def test_order_confirm(self):
        self.client.force_authenticate(user=self.user1)
        url = ('/orders/%s/confirm/' % self.order1.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order1.refresh_from_db()
        self.assertEqual(self.order1.status, 'PROCESS')

    def test_order_confirm_fail(self):
        self.client.force_authenticate(user=self.user2)
        url = ('/orders/%s/confirm/' % self.order1.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
