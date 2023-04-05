from django.db import models
# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator


User = get_user_model()


class Category(models.Model):
    title = models.CharField(max_length=40)
    slug = models.SlugField(max_length=40)
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        return self.title



class Product(models.Model):
    user = models.ForeignKey(User, related_name='products', on_delete=models.CASCADE)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50)
    image = models.ImageField(upload_to='products', null=True)
    price = models.IntegerField()
    description = models.TextField()
    is_sold = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    product_id = models.ForeignKey('Category', on_delete=models.PROTECT, null=True)


    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = "Продукты"
    
    def __str__(self) -> str:
        return self.title
    

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(
        auto_now=True
    )
    title = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')

    class Meta:
        verbose_name = 'Коментарий'
        verbose_name_plural = 'Коментарии'
    
    def __str__(self) -> str:
        return f'Коментарий от {self.user.username}'
    
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    title = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        verbose_name = 'Лайк'
        verbose_name_plural = 'Лайки'
        

    def __str__(self) -> str:
        return f'Liked by {self.username}'
        
class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    title = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    rate = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
        
    def __str__(self) -> str:
        return str(self.rate)
    
    class Meta:
        verbose_name = 'Рейтинг'
        verbose_name_plural = 'Рейтинги'
        