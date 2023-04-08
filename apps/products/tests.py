from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from .models import Product, Category
from .serializers import ProductSerializer

User = get_user_model()


class ProductViewSetTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass',
            email='test@test.com')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(
            title='Test category')
        self.product_data = {
            'title': 'Test Product',
            'price': 100,
            'description': 'This is a test product',
            'categories': [1]}

    def test_create_product(self):
        response = self.client.post('/products/', self.product_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 1)
        self.assertEqual(Product.objects.get().title, 'Test Product')

    def test_retrieve_single_product(self):
        product = Product.objects.create(
            user=self.user, title='Test Product', price=100,
            description='This is a test product')
        response = self.client.get(f'/products/{product.pk}/')
        response.data['image'] = f'/media/{product.image.name}'
        serializer = ProductSerializer(product)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_product(self):
        product = Product.objects.create(
            user=self.user, title='Test Product', price=100,
            description='This is a test product')
        update_data = {
            'title': 'New Test Product',
            'price': 200,
            'description': 'This is a new test product',
        }
        response = self.client.patch(
            f'/products/{product.pk}/', update_data)
        response.data['image'] = f'/media/{product.image.name}'
        product.refresh_from_db()
        serializer = ProductSerializer(product)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_product(self):
        product = Product.objects.create(
            user=self.user, title='Test Product', price=100,
            description='This is a test product')
        response = self.client.delete(f'/products/{product.pk}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Product.objects.count(), 0)
