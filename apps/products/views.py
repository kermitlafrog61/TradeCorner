from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ProductSerializer
from .models import Product
from rest_framework.views import APIView

class ProductAPIView(APIView):
    def get(self, request):
        all_products = Product.objects.all()
        return Response({'posts': ProductSerializer(all_products, many=True).data})
    
    def create_post(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'post': serializer.data})
    
    def get_new_product(self, request, *arg, **kwargs):
        pk = kwargs.get('pk', None)
        if not pk:
            return Response({'Ошибка': 'Метод не отвечает'})
        try:
            instance = Product.objects.get(pk=pk)
        except:
            return Response({'Ошибка': 'Продукт не существует'})
        
        serializer = ProductSerializer(data=request.data, instance=instance)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'post': serializer.data})
    
    def delete(self, request, *arg, **kwargs):
        pk = kwargs.get('pk', None)
        if not pk:
            return Response({'Ошибка': 'Метод не удаляется'})
        try:
            instance = Product.objects.get(pk=pk)
            instance.delete()
        except:
            return Response({'post': 'delete post ' + str(pk)})
    
    




