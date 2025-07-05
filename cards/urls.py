from django.urls import path
from . import views

urlpatterns = [
    path('', views.CartDetailView.as_view(), name='cart-detail'),
    path('items/', views.AddToCartView.as_view(), name='add-to-cart'),
    path('items/<int:pk>/', views.UpdateCartItemView.as_view(), name='update-cart-item'),  # برای به‌روزرسانی مقدار
    path('items/<int:pk>/remove/', views.RemoveFromCartView.as_view(), name='remove-from-cart'),  # برای حذف
    path('clear/', views.ClearCartView.as_view(), name='clear-cart'),
]