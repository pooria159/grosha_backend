from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.utils import timezone
from sellers.models import Seller

class Ticket(models.Model):
    STATUS_CHOICES = [
        ('open', 'باز'),
        ('in_progress', 'در حال بررسی'),
        ('answered', 'پاسخ داده شده'),
        ('closed', 'بسته شده'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'کم'),
        ('medium', 'متوسط'),
        ('high', 'بالا'),
    ]
    
    CATEGORY_CHOICES = [
        ('technical', 'فنی'),
        ('financial', 'مالی'),
        ('order', 'سفارش'),
        ('other', 'سایر'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='technical')
    order_id = models.CharField(max_length=50, blank=True, null=True)
    admin_notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_status_display(self):
        return dict(self.STATUS_CHOICES).get(self.status)

    def get_priority_display(self):
        return dict(self.PRIORITY_CHOICES).get(self.priority)

    def get_category_display(self):
        return dict(self.CATEGORY_CHOICES).get(self.category)

    def __str__(self):
        return f"تیکت {self.id} - {self.subject}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'تیکت'
        verbose_name_plural = 'تیکت‌ها'


class TicketReply(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='replies')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    message = models.TextField()
    is_staff_reply = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"پاسخ {self.id} به تیکت {self.ticket.id}"

    class Meta:
        ordering = ['created_at']
        verbose_name = 'پاسخ تیکت'
        verbose_name_plural = 'پاسخ‌های تیکت'


class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name='تلفن همراه')
    username = models.TextField(max_length=30 ,unique=True , blank=True , null=True , verbose_name='نام کاربری')

    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'

class Discount(models.Model):
    seller = models.ForeignKey(
        Seller, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='discounts',
        verbose_name='فروشگاه'
    )
    title = models.CharField(max_length=255, verbose_name='عنوان')
    code = models.CharField(max_length=50, unique=True, verbose_name='کد تخفیف')
    description = models.TextField(verbose_name='توضیحات', blank=True)
    percentage = models.PositiveIntegerField(verbose_name='درصد تخفیف')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    for_first_purchase = models.BooleanField(
        default=False, 
        verbose_name='فقط اولین خرید'
    )
    is_single_use = models.BooleanField(
        default=True,
        verbose_name='یکبار مصرف'
    )
    valid_from = models.DateTimeField(
        default=timezone.now,
        verbose_name='تاریخ شروع اعتبار'
    )
    valid_to = models.DateTimeField(
        verbose_name='تاریخ پایان اعتبار',
        default= timezone.now
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ به‌روزرسانی')
    min_order_amount = models.PositiveIntegerField(
        default=0,
        verbose_name='حداقل مبلغ سفارش'
    )

    class Meta:
        verbose_name = 'تخفیف'
        verbose_name_plural = 'تخفیف‌ها'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['is_active']),
            models.Index(fields=['valid_to']),
        ]

    def __str__(self):
        return f"{self.title} ({self.percentage}%) - {self.seller.shop_name if self.seller else 'عمومی'}"

    def is_valid(self):
        now = timezone.now()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_to
        )

    def remaining_time(self):
        now = timezone.now()
        if now > self.valid_to:
            return "منقضی شده"
        
        remaining = self.valid_to - now
        days = remaining.days
        hours, remainder = divmod(remaining.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days} روز و {hours} ساعت"
        elif hours > 0:
            return f"{hours} ساعت و {minutes} دقیقه"
        return f"{minutes} دقیقه"

class BankCard(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bank_cards')
    card_name = models.CharField(max_length=100, verbose_name="نام کارت")
    card_number = models.CharField(max_length=16, verbose_name="شماره کارت")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.card_name}"

class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='addresses')
    title = models.CharField(max_length=100, default='آدرس جدید')
    address_line = models.TextField()
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"