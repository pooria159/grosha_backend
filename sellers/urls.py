from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    SellerSettingsView,
    ShippingMethodCreateView,
    ShippingMethodDeleteView,
    PaymentGatewayCreateView,
    PaymentGatewayDeleteView,
    SellerRegister,
    SellerLogin,
    Check_shop
    
)

urlpatterns = [
    path('register/', SellerRegister.as_view()),
    path('login/', SellerLogin.as_view()),
    path('check-shop/', Check_shop , name='check_shop'),
    path('settings/', SellerSettingsView.as_view(), name='seller-settings'),
    path('shipping-methods/', ShippingMethodCreateView.as_view(), name='shipping-method-create'),
    path('shipping-methods/<int:id>/', ShippingMethodDeleteView.as_view(), name='shipping-method-delete'),
    path('payment-gateways/', PaymentGatewayCreateView.as_view(), name='payment-gateway-create'),
    path('payment-gateways/<int:id>/', PaymentGatewayDeleteView.as_view(), name='payment-gateway-delete'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
