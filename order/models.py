from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product

User = get_user_model()

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در حال پردازش'),
        ('completed', 'تحویل شده'),
        ('cancelled', 'لغو شده'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.IntegerField(default=0)
    original_price = models.IntegerField(default=0)
    discount = models.ForeignKey(
        'users.Discount', 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )
    
    class Meta:
        ordering = ['-created_at']
        
    def update_total(self):
        self.original_price = sum(item.price * item.quantity for item in self.items.all())
        if self.discount:
            self.total_price = int(self.original_price * (1 - self.discount.percentage / 100))
        else:
            self.total_price = self.original_price

        self.save()
        
    class Meta:
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارش ها'

    def __str__(self):
        return f"سفارش {self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name='سفارش')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, verbose_name='محصول')
    seller = models.ForeignKey('sellers.Seller', on_delete=models.PROTECT, null=True, blank=True, verbose_name='فروشنده')
    quantity = models.PositiveIntegerField(verbose_name='تعداد')
    price = models.IntegerField(verbose_name='قیمت')
    
    class Meta:
        unique_together = ['order', 'product', 'seller']
        verbose_name = 'آیتم سفارش'
        verbose_name_plural = 'آیتم‌های سفارش'
    
    def __str__(self):
        return f"{self.product.name} ({self.quantity}) - {self.order}"