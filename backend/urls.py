from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from users.views import CustomTokenObtainPairView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('users.urls')), 
    path('api/', include('team_management.urls')),
    path('api/users/', include('users.urls')),
    path('api/sellers/', include('sellers.urls')),
    path('api/products/', include('products.urls')),
    path('api/orders/', include('order.urls')),
    path('api/cart/' , include('cards.urls')),

    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)