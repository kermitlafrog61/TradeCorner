from django.contrib import admin
from .models import Category, Product, Comment, Like, Rating 


admin.site.register([Category, Product, Comment, Like, Rating])
