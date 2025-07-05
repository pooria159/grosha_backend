from django.db import models
from django.conf import settings

class Seller(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='seller')
    shop_name = models.CharField(max_length=255, verbose_name="نام فروشگاه")
    logo = models.ImageField(upload_to='shop_logos/', null=True, blank=True, verbose_name="لوگو فروشگاه")
    phone = models.CharField(max_length=15, verbose_name="تلفن")
    address = models.TextField(verbose_name="آدرس")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    min_order_amount = models.PositiveIntegerField(default=100000, verbose_name="حداقل مبلغ سفارش")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    
    def __str__(self):
        return self.shop_name

    class Meta:
        verbose_name = 'فروشنده'
        verbose_name_plural = 'فروشندگان'


class ShippingMethod(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='shipping_methods')
    name = models.CharField(max_length=100, verbose_name="نام روش ارسال")
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'روش ارسال'
        verbose_name_plural = 'روش‌های ارسال'


class PaymentGateway(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='payment_gateways')
    name = models.CharField(max_length=100, verbose_name="نام درگاه پرداخت")
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'درگاه پرداخت'
        verbose_name_plural = 'درگاه‌های پرداخت'