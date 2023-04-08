from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Order
from .utils import create_activation_code
from apps.products.models import Product

User = get_user_model()


class OrderTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='testuser1', password='testpass123', email='test1@test.com')
        self.user2 = User.objects.create_user(
            username='testuser2', password='testpass123', email='test2@test.com')
        self.product = Product.objects.create(
            title='Test Product', description='Test description',
            price=10, user=self.user1)
        self.order1 = Order.objects.create(
            user=self.user2, product=self.product, address='Test address 1')

    def test_create_order(self):
        id = self.order1.id + 1
        self.order1.delete()
        self.client.force_authenticate(user=self.user2)
        url = ('/products/%s/order/' % self.product.id)
        data = {'address': 'Test address 3'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(Order.objects.get(pk=id).user, self.user2)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_order_status(self):
        self.client.force_authenticate(user=self.user1)
        url = ('/orders/%s/' % self.order1.id)
        data = {'status': 'DELIVER'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_206_PARTIAL_CONTENT)
        self.assertEqual(Order.objects.get(
            id=self.order1.id).status, 'DELIVER')

    def test_update_order_status_with_invalid_data(self):
        self.client.force_authenticate(user=self.user2)
        url = ('/orders/%s/' % self.order1.id)
        data = {'status': 'PROCESS'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_order(self):
        self.client.force_authenticate(user=self.user2)
        url = ('/orders/%s/' % self.order1.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Order.objects.count(), 1)

    def test_delete_order_with_unauthorized_user(self):
        url = ('/orders/%s/' % self.order1.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Order.objects.count(), 1)


class OrderCompleteTestCase(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='testuser1', password='testpass123', email='test1@test.com')
        self.user2 = User.objects.create_user(
            username='testuser2', password='testpass123', email='test2@test.com')
        self.product = Product.objects.create(
            title='Test Product', description='Test description',
            price=10, user=self.user1)
        self.order1 = Order.objects.create(
            user=self.user2, product=self.product,
            address='Test address 1', status='DELIVER')
        create_activation_code(self.order1)
        self.url_complete = reverse('complete', args=[self.order1.activation_code])
        self.url_confirm = reverse('confirm', args=[self.order1.activation_code])

    def test_order_complete(self):
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.url_complete)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order1.refresh_from_db()
        self.assertEqual(self.order1.status, 'COMPLETE')
        self.assertEqual(self.order1.activation_code, '')

    def test_order_confirm(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.url_confirm)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order1.refresh_from_db()
        self.assertEqual(self.order1.status, 'PROCESS')
        self.assertEqual(self.order1.activation_code, '')
