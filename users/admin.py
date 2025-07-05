from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Discount, Ticket, TicketReply

class TicketReplyInline(admin.StackedInline):
    model = TicketReply
    extra = 0
    readonly_fields = ('user', 'created_at')
    fields = ('user', 'message', 'created_at')

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'subject', 'status', 'priority', 'category', 'created_at')
    list_filter = ('status', 'priority', 'category', 'created_at')
    search_fields = ('subject', 'message', 'user__username', 'order_id')
    readonly_fields = ('created_at', 'updated_at')
    list_editable = ('status', 'priority')
    inlines = [TicketReplyInline]
    fieldsets = (
        (None, {'fields': ('user', 'subject', 'message')}),
        ('مشخصات فنی', {'fields': ('status', 'priority', 'category', 'order_id')}),
        ('یادداشت مدیریت', {'fields': ('admin_notes',)}),
        ('تاریخ‌ها', {'fields': ('created_at', 'updated_at')}),
    )

@admin.register(TicketReply)
class TicketReplyAdmin(admin.ModelAdmin):
    list_display = ('id', 'ticket', 'user', 'short_message', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('message', 'ticket__subject')
    readonly_fields = ('created_at',)

    def short_message(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    short_message.short_description = 'پیام'

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('id', 'username', 'email', 'phone', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'phone')
    ordering = ('id',)
    list_display_links = ('id', 'username')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('اطلاعات شخصی', {'fields': ('email', 'phone', 'first_name', 'last_name')}),
        ('سطوح دسترسی', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('تاریخ‌ها', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'code', 'seller', 'percentage', 'is_active', 'created_at', 'remaining_time')
    list_filter = ('is_active', 'for_first_purchase', 'seller', 'created_at')
    search_fields = ('title', 'code', 'seller__user__username')
    readonly_fields = ('remaining_time',)
    list_select_related = ('seller', 'seller__user')

    def remaining_time(self, obj):
        return obj.remaining_time()
    remaining_time.short_description = 'زمان باقی‌مانده'