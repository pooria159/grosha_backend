from rest_framework import serializers
from .models import Cart, CartItem

class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = [
            'id',
            'product_id',
            'seller_id',
            'quantity',
            'product_name',
            'product_price',
            'product_stock',
            'product_image',
            'store_name',
            'added_at'
        ]
        read_only_fields = [
            'id',
            'product_name',
            'product_price',
            'product_image',
            'product_stock',
            'store_name',
            'added_at'
        ]

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("تعداد باید حداقل ۱ باشد")
        return value


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_price = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = [
            'id',
            'user',
            'created_at',
            'updated_at',
            'items',
            'total_items',
            'total_price'
        ]
        read_only_fields = [
            'id',
            'user',
            'created_at',
            'updated_at',
            'total_items',
            'total_price'
        ]


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(min_value=1)
    seller_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1, default=1)