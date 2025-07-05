from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'quantity', 'price', 'seller']
    fields = ['product', 'quantity', 'price', 'seller']
    can_delete = False

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_price', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'user__email', 'id']
    readonly_fields = ['user', 'total_price', 'created_at', 'updated_at']
    inlines = [OrderItemInline]

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order', 'product', 'quantity', 'price', 'seller']
    list_filter = ['seller']
    search_fields = ['order__id', 'product__name', 'seller__name']
    readonly_fields = ['order', 'product', 'quantity', 'price', 'seller']