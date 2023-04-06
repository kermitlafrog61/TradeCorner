from django.urls import path
from knox.views import LogoutView

from . import views
from apps.orders.views import OrderOwnerList


urlpatterns = [
    path('', views.UserAPI.as_view()),
    path('registration/', views.Registration.as_view()),
    path('activate/<str:activation_code>/', views.Activation.as_view(), name='activate'),
    path('login/', views.LoginAPI.as_view()),
    path('logout/', LogoutView.as_view()),
    path('change-password/', views.PasswordUpdate.as_view()),
    path('restore-password/', views.PasswordRestore.as_view()),
    path('orders/', OrderOwnerList.as_view())
]
