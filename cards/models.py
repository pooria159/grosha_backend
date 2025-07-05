from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

User = get_user_model()

class Cart(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='cart',
        verbose_name='کاربر'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ به‌روزرسانی')

    class Meta:
        verbose_name = 'سبد خرید'
        verbose_name_plural = 'سبدهای خرید'

    def __str__(self):
        return f"سبد خرید کاربر {self.user.username}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        return sum(item.product_price * item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='سبد خرید'
    )
    product_id = models.PositiveIntegerField(verbose_name='شناسه محصول')
    seller_id = models.PositiveIntegerField(verbose_name='شناسه فروشنده')
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='تعداد'
    )
    product_name = models.CharField(max_length=255, verbose_name='نام محصول')
    product_price = models.PositiveIntegerField(verbose_name='قیمت محصول')
    product_stock = models.PositiveIntegerField(verbose_name='تعداد محصولات', default=True)
    product_image = models.URLField(blank=True, null=True, verbose_name='تصویر محصول')
    store_name = models.CharField(max_length=255, verbose_name='نام فروشگاه')
    added_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ افزودن')

    class Meta:
        verbose_name = 'آیتم سبد خرید'
        verbose_name_plural = 'آیتم‌های سبد خرید'
        unique_together = ('cart', 'product_id', 'seller_id')

    def __str__(self):
        return f"{self.quantity} عدد {self.product_name} از {self.store_name}"