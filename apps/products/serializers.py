from rest_framework import serializers
from .models import Product



class ProductSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=50)
    slug = serializers.SlugField(max_length=50)
    image = serializers.ImageField()
    price = serializers.IntegerField()
    description = serializers.CharField()
    is_sold = serializers.BooleanField()
    created_at = serializers.DateField(read_only=True)
    updated_at = serializers.DateField(read_only=True)
    product_id = serializers.ImageField()

    def create(self, validated_data):
        return Product.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.slug = validated_data.get('slug', instance.slug)
        instance.image = validated_data.get('image', instance.image)
        instance.price = validated_data.get('price', instance.price)
        instance.description = validated_data.get('description', instance.description)
        instance.is_sold = validated_data.get('is_sold', instance.is_sold)
        instance.created_at = validated_data.get('created_at', instance.created_at)
        instance.updated_at = validated_data.get('updated_at', instance.updated_at)
        instance.product_id = validated_data.get('product_id', instance.product_id)
        instance.save()
        return instance
    
