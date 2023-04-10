from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
    openapi.Info(
        title='TradeCorner API',
        default_version='v1',
        description='API for marketplace',
        terms_of_service='https://google.com/policies/terms/',
        contact=openapi.Contact(email='contact@snippets.local'),
        license=openapi.License(name='BSD License')
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    path('', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.users.urls'), name='user accounts api'),
    path('', include('apps.orders.urls')),
    path('', include('apps.products.urls')),
]

urlpatterns += staticfiles_urlpatterns()
