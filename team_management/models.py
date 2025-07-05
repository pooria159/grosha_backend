from django.db import models
from django.conf import settings
from sellers.models import Seller

class StoreRole(models.Model):
    ROLE_CHOICES = [
        ('cashier', 'صندوق دار'),
        ('warehouse', 'انباردار'),
        ('support', 'پشتیبان'),
        ('manager', 'مدیر فروشگاه'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='store_roles'
    )
    seller = models.ForeignKey(
        Seller,
        on_delete=models.CASCADE,
        related_name='store_roles'
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'seller')
        verbose_name = 'نقش فروشگاه'
        verbose_name_plural = 'نقش‌های فروشگاه'

    def __str__(self):
        return f"{self.user.username} - {self.seller.shop_name} ({self.get_role_display()})"