from rest_framework import serializers
from sellers.models import PaymentGateway, Seller, ShippingMethod
import base64
from django.core.files.base import ContentFile
import uuid

class ShippingMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingMethod
        fields = ['id', 'name']

class PaymentGatewaySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentGateway
        fields = ['id', 'name']

class SellerSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    stock = serializers.SerializerMethodField()
    shipping_methods = ShippingMethodSerializer(many=True, read_only=True)
    payment_gateways = PaymentGatewaySerializer(many=True, read_only=True)
    logo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Seller
        fields = [
            'id', 'shop_name', 'logo', 'phone', 'address', 
            'description', 'min_order_amount', 'is_active',
            'shipping_methods', 'payment_gateways', 'price', 'stock'
        ]
        extra_kwargs = {
            'logo': {'write_only': True, 'required': False, 'allow_null': True}
        }
        
    def get_price(self, obj):
        product = self.get_related_product(obj)
        return product.price if product else None

    def get_stock(self, obj):
        product = self.get_related_product(obj)
        return product.stock if product else 0

    def get_related_product(self, obj):
        product_name = self.context.get('product_name')
        category_id = self.context.get('category_id')
        subcategory_id = self.context.get('subcategory_id')
        
        return obj.product_set.filter(
            name=product_name,
            category_id=category_id,
            subcategory_id=subcategory_id
        ).first()
        
    def to_internal_value(self, data):
        if 'logo' in data and isinstance(data['logo'], str) and data['logo'].startswith('data:image'):
            try:
                format, imgstr = data['logo'].split(';base64,')
                ext = format.split('/')[-1]
                
                filename = f"{uuid.uuid4()}.{ext}"
                data['logo'] = ContentFile(
                    base64.b64decode(imgstr),
                    name=filename
                )
            except Exception as e:
                raise serializers.ValidationError({
                    'logo': 'فرمت تصویر نامعتبر است'
                })

        return super().to_internal_value(data)