from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Category, Subcategory, Product,ProductComment
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']

class ProductCommentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_id = serializers.IntegerField(source='product.id', read_only=True)

    class Meta:
        model = ProductComment
        fields = ['id', 'user', 'product_name', 'product_id', 'text', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'product_name', 'product_id', 'created_at', 'updated_at']


class CreateProductCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductComment
        fields = ['text']

 
class ProductSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name')
    subcategory = serializers.CharField(source='subcategory.name')
    category_id = serializers.SerializerMethodField()
    subcategory_id = serializers.SerializerMethodField()
    sellers_count = serializers.SerializerMethodField()
    sellers = serializers.SerializerMethodField()
    product_group_id = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'category', 'subcategory', 'category_id', 
                'subcategory_id', 'price', 'stock', 'sellers', 'sellers_count',
                'product_group_id']
        read_only_fields = ['id']
    
    def get_product_group_id(self, obj):
        return f"{obj.name}-{obj.category.id}-{obj.subcategory.id}".lower().replace(' ', '-')
        
    def get_sellers_count(self, obj):
        return Product.objects.filter(
            name=obj.name,
            category=obj.category,
            subcategory=obj.subcategory
        ).count()

    def get_sellers(self, obj):
        similar_products = Product.objects.filter(
            name=obj.name,
            category=obj.category,
            subcategory=obj.subcategory
        ).select_related('seller')
        
        sellers_data = []
        for product in similar_products:
            sellers_data.append({
                'seller_id': product.seller.id,
                'shop_name': product.seller.shop_name,
                'price': product.price,
                'stock': product.stock,
                'product_id': product.id
            })
        return sellers_data

    def get_category_id(self, obj):
        return obj.category.id if obj.category else None

    def get_subcategory_id(self, obj):
        return obj.subcategory.id if obj.subcategory else None

    def validate(self, data):
        category_name = data.get('category', {}).get('name', '').strip()
        subcategory_name = data.get('subcategory', {}).get('name', '').strip()
        product_name = data.get('name', '').strip()
        request = self.context.get('request')
        instance = getattr(self, 'instance', None)

        if category_name and subcategory_name and product_name:
            try:
                category = Category.objects.get(name=category_name)
                subcategory = Subcategory.objects.get(name=subcategory_name, category=category)

                if not instance and Product.objects.filter(
                    name=product_name,
                    category=category,
                    subcategory=subcategory,
                    seller=request.user.seller
                ).exists():
                    raise ValidationError(
                        "شما قبلاً این محصول را در همین دسته‌بندی ثبت کرده‌اید."
                    )

            except (Category.DoesNotExist, Subcategory.DoesNotExist):
                pass

        return data

    def create(self, validated_data):
        category_name = validated_data.pop('category', {}).get('name', '').strip()
        subcategory_name = validated_data.pop('subcategory', {}).get('name', '').strip()
        request = self.context.get('request')

        category, _ = Category.objects.get_or_create(name=category_name)
        subcategory, _ = Subcategory.objects.get_or_create(
            name=subcategory_name, category=category
        )

        validated_data.pop('seller', None)

        product = Product.objects.create(
            seller=request.user.seller,
            category=category,
            subcategory=subcategory,
            **validated_data
        )
        return product
    
    
    def update(self, instance, validated_data):
        category_name = validated_data.get('category', {}).get('name', '').strip()
        subcategory_name = validated_data.get('subcategory', {}).get('name', '').strip()
        request = self.context.get('request')

        if category_name:
            category, _ = Category.objects.get_or_create(name=category_name)
            instance.category = category

        if subcategory_name:
            subcategory, _ = Subcategory.objects.get_or_create(
                name=subcategory_name, category=instance.category
            )
            instance.subcategory = subcategory

        instance.name = validated_data.get('name', instance.name)
        instance.price = validated_data.get('price', instance.price)
        instance.stock = validated_data.get('stock', instance.stock)
        instance.save()
        return instance
    
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = ['id', 'name', 'category']