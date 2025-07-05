from django.contrib import admin
from .models import Cart, CartItem

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_items', 'total_price', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')

    def total_items(self, obj):
        return obj.total_items
    total_items.short_description = 'تعداد آیتم‌ها'

    def total_price(self, obj):
        return f"{obj.total_price:,} تومان"
    total_price.short_description = 'جمع کل'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'store_name', 'quantity', 'product_price', 'cart_user')
    list_filter = ('store_name',)
    search_fields = ('product_name', 'store_name', 'cart__user__username')
    readonly_fields = ('added_at',)

    def cart_user(self, obj):
        return obj.cart.user.username
    cart_user.short_description = 'کاربر'