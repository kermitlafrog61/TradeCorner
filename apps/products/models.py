from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator


User = get_user_model()


class Category(models.Model):
    title = models.CharField(max_length=40)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self) -> str:
        return self.title


class Product(models.Model):
    user = models.ForeignKey(
        User, related_name='products', on_delete=models.CASCADE)
    category = models.ForeignKey(
        Category, related_name='products', on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    image = models.ImageField(default='default.jpg',
                              upload_to='product_images')
    price = models.IntegerField()
    description = models.TextField()
    is_sold = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)


    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = "Продукты"

    def __str__(self) -> str:
        return self.title


class Comment(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Коментарий'
        verbose_name_plural = 'Коментарии'

    def __str__(self) -> str:
        return f'Коментарий от {self.user.username}'


class Like(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='likes')
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        verbose_name = 'Лайк'
        verbose_name_plural = 'Лайки'

    def __str__(self) -> str:
        return f'Liked by {self.username}'


class Rating(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='ratings')
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='ratings')
    rate = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)])

    def __str__(self) -> str:
        return str(self.rate)

    class Meta:
        verbose_name = 'Рейтинг'
        verbose_name_plural = 'Рейтинги'
