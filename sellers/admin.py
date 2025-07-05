from django.contrib import admin
from .models import Seller

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ['id', 'shop_name', 'phone', 'user']
    search_fields = ['shop_name', 'phone', 'user__username', 'user__email']
    list_filter = ['shop_name']
    autocomplete_fields = ['user']
    list_display_links = ['id', 'shop_name']
    ordering = ['shop_name']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')