from django.contrib import admin
from .models import StoreRole

@admin.register(StoreRole)
class StoreRoleAdmin(admin.ModelAdmin):
    list_display = ('user', 'seller', 'role', 'is_active', 'created_at')
    search_fields = ('user__username', 'seller__shop_name')
    list_filter = ('role', 'is_active', 'seller')