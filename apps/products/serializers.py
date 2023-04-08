from PIL import Image
from django.db.models import Avg
from django.core.files.storage import default_storage
from rest_framework import serializers

from .models import Product
from apps.users.serializers import UserSerializer
from .models import Comment, Rating, Like, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'title')


class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'id', 'categories', 'user', 'title', 'ratings',
            'ratings', 'image', 'price', 'is_sold')

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['user'] = UserSerializer(instance.user).data
        repr['categories'] = [
            category.title for category in instance.categories.all()]
        repr['ratings'] = (instance
                           .ratings
                           .aggregate(Avg('rate'))['rate__avg'])
        return repr


class ProductSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    orders_count = serializers.SerializerMethodField(method_name='get_orders_count')
    likes = serializers.SerializerMethodField(method_name='get_likes_count')


    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = (
            'id', 'user', 'comments', 'orders_count')

    def get_orders_count(self, product):
        return product.orders.count()
    
    def get_likes_count(self, product):
        return product.likes.count()

    def create(self, validated_data):
        image_path = validated_data.get('image')
        if image_path:
            image = Image.open(image_path)

            if image.height > 300 or image.width > 300:
                image.thumbnail((300, 300))

                with default_storage.open(image_path.name, 'wb') as f:
                    image.save(f, format=image.format)

        return super().create(validated_data)

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['user'] = UserSerializer(instance.user).data
        repr['categories'] = [
            category.title for category in instance.categories.all()]
        repr['comments'] = CommentSerializer(
            instance.comments.all(), many=True).data
        repr['ratings'] = (instance
                           .ratings
                           .aggregate(Avg('rate'))['rate__avg'])
        return repr


class LikeSerializer:
    def __init__(self, user, product, **kwargs):
        like = Like.objects.filter(user=user, product=product)
        
        if like.exists():
            like.delete()
            self.data = {'liked': False}
        else:
            Like.objects.create(user=user, product=product).save()
            self.data = {'liked': True}


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Comment
        fields = ('id', 'user', 'product',
                  'text', 'created_at')
        read_only_fields = ('product',)


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ('id', 'user', 'product', 'rate')
        read_only_fields = ('user', 'product')

    def validate(self, attrs):
        user = self.context.get('request').user
        product = self.context.get('product')
        rate = Rating.objects.filter(user=user, product=product)
        if rate:
            raise serializers.ValidationError(
                {'message': 'Rate already exists'})
        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)
