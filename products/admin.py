from django.contrib import admin
from .models import Product, Category, Subcategory,ProductComment

@admin.register(ProductComment)
class ProductCommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'user', 'created_at']
    list_filter = ['product', 'user']
    search_fields = ['text', 'user__username', 'product__name']
    list_select_related = ['product', 'user']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']
    search_fields = ['name']
    list_display_links = ['id', 'name']
    ordering = ['name']

@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category']
    list_filter = ['category']
    search_fields = ['name', 'category__name']
    list_select_related = ['category']
    list_display_links = ['id', 'name']
    ordering = ['category__name', 'name']
    autocomplete_fields = ['category']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category', 'subcategory', 'price', 'stock', 'seller']
    list_filter = ['category', 'subcategory', 'seller']
    search_fields = ['name', 'category__name', 'subcategory__name', 'seller__shop_name']
    list_select_related = ['category', 'subcategory', 'seller']
    list_display_links = ['id', 'name']
    ordering = ['name']
    autocomplete_fields = ['category', 'subcategory', 'seller']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'category', 'subcategory', 'seller', 'seller__user'
        )