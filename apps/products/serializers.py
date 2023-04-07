from PIL import Image
from rest_framework import serializers

from .models import Product
from apps.users.serializers import UserSerializer
from django.db.models import Avg
from .models import Comment, Rating, Like, Category


class LikeSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Like
        fields = ('user',)


class ProductSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Product
        fields = (
            'id', 'category', 'user', 'title', 'comments',
            'image', 'price', 'description', 'is_sold')
        read_only_fields = (
            'id', 'user', 'comments')

    def create(self, validated_data):
        validated_data['user'] = self.context.get('request').user
        img = Image.open(validated_data['image'].path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)
            
        return super().create(validated_data)

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['user'] = UserSerializer(instance.user).data
        repr['category'] = instance.category.title
        repr['comments'] = CommentSerializer(
            instance.comments.all(), many=True).data
        repr['ratings'] = (instance
                        .ratings
                        .aggregate(Avg('rate'))['rate__avg'])
        return repr


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Comment
        fields = ('id', 'user', 'product',
                  'text','created_at')
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


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = 'all'
