from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Order, OrderItem
from sellers.models import Seller
from products.serializers import ProductSerializer

User = get_user_model()

class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = ['id', 'shop_name', 'phone']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    seller = SellerSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price', 'seller']

class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    discount_percentage = serializers.SerializerMethodField()
    discount_code = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'user', 'items', 'total_price', 'original_price', 
                 'status', 'created_at', 'discount', 'discount_percentage', 'discount_code']

    def get_discount_percentage(self, obj):
        return obj.discount.percentage if obj.discount else None

    def get_discount_code(self, obj):
        return obj.discount.code if obj.discount else None